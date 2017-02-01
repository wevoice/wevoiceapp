import json
import openpyxl
import os
import traceback
from collections import OrderedDict
from copy import deepcopy
from django import forms
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.transaction import TransactionManagementError
from django.utils.translation import ugettext_lazy as _
from import_export import fields
from import_export import resources
from import_export.resources import Diff
from import_export.results import Result, RowResult
from import_export.widgets import ForeignKeyWidget
from import_export.forms import ImportForm, ConfirmImportForm
from import_export.instance_loaders import ModelInstanceLoader
from import_export.tmp_storages import TempFolderStorage
from tablib import Dataset
from . import models
from .forms import BaseAudioForm


# Set default logging handler to avoid "No handler found" warnings.
import logging  # isort:skip
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())


class ImportFormWithSamples(ImportForm):
    sample_files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}, ),
        label=_('Sample Files'),
        required=False
    )


class ConfirmImportFormWithSamples(ConfirmImportForm):
    sample_files_dict = forms.CharField(widget=forms.HiddenInput())

    def clean_sample_files_dict(self):
        return json.loads(self.cleaned_data['sample_files_dict'])


class ModelInstanceLoaderWithSamples(ModelInstanceLoader):
    """
    Instance loader for Django model.

    Lookup for model instance by ``import_id_fields``.
    """

    def get_queryset(self):
        return self.resource._meta.model.objects.all()

    def get_instance(self, row):
        try:
            params = {}
            for key in self.resource.get_import_id_fields():
                field = self.resource.fields[key]
                params[field.attribute] = field.clean(row)
            return self.get_queryset().get(**params)
        except self.resource._meta.model.DoesNotExist:
            return None


def new_row_result_init(self):
    self.errors = []
    self.diff = None
    self.talent_obj = None
    self.import_type = None
    self.update_talent = None
    self.replace_talent = None

RowResult.IMPORT_TYPE_DUPLICATE = 'duplicate'
RowResult.IMPORT_TYPE_REPLACE = 'replace'
RowResult.IMPORT_TYPE_UPDATE_WELO_ID = 'update_welo_id'
RowResult.__init__ = new_row_result_init


def new_result_init(self, *args, **kwargs):
    super(Result, self).__init__()
    self.args = args
    self.kwargs = kwargs
    self.base_errors = []
    self.diff_headers = []
    self.rows = []  # RowResults
    self.failed_dataset = Dataset()
    self.totals = OrderedDict([(RowResult.IMPORT_TYPE_NEW, 0),
                               (RowResult.IMPORT_TYPE_UPDATE, 0),
                               (RowResult.IMPORT_TYPE_UPDATE_WELO_ID, 0),
                               (RowResult.IMPORT_TYPE_DELETE, 0),
                               (RowResult.IMPORT_TYPE_SKIP, 0),
                               (RowResult.IMPORT_TYPE_DUPLICATE, 0),
                               (RowResult.IMPORT_TYPE_REPLACE, 0),
                               (RowResult.IMPORT_TYPE_ERROR, 0)])
    self.total_rows = 0

Result.__init__ = new_result_init


class TalentResource(resources.ModelResource):
    sample_files_dict = {}
    file_actions_dict = {'skip_import': [], 'duplicate': [], 'replace': {}, 'update_welo_id': {}, 'new': {}}
    retrieved_sample_files_dict = {}

    def create_samples_dataset(self, in_stream):
        """
        Create import dictionary from first sheet.
        """
        from io import BytesIO
        xlsx_book = openpyxl.load_workbook(BytesIO(in_stream), read_only=True)
        sheet = xlsx_book.active
        rows = sheet.rows
        for row in rows:
            # File is missing from uploaded fileset
            if not row[0].value in self.sample_files_dict:
                self.file_actions_dict['skip_import'].append(row[0].value)
            else:
                existing_talent = models.Talent.objects.filter(audio_file=row[0].value)
                import_file_sha = BaseAudioForm.current_file_sha(File(open(self.sample_files_dict[row[0].value])))
                t_with_matching_file_sha = models.Talent.objects.filter(audio_file_sha=import_file_sha)
                if existing_talent.exists():
                    # Talent with same name and content already exists
                    if import_file_sha and import_file_sha == existing_talent[0].audio_file_sha:
                        self.sample_files_dict.pop(row[0].value, None)
                        self.file_actions_dict['duplicate'].append(row[0].value)
                    # Talent with same name but different content already exists
                    else:
                        self.file_actions_dict['replace'][row[0].value] = existing_talent[0].welo_id
                # Talent with same content but different name already exists
                elif t_with_matching_file_sha and t_with_matching_file_sha.exists():
                    self.file_actions_dict['update_welo_id'][row[0].value] = t_with_matching_file_sha[0].welo_id
                else:
                    self.file_actions_dict['new'][row[0].value] = import_file_sha

    def retrieve_stored_sample_files(self):
        self.retrieved_sample_files_dict = {}
        for key, value in self.sample_files_dict.items():
            if key != 'file_actions':
                retrieved_sample_file = TempFolderStorage(name=value)
                data = retrieved_sample_file.read('rb')
                self.retrieved_sample_files_dict[key] = data

    def save_sample_files(self, sample_files):
        for sample_file in sample_files:
            samples_tmp_storage = TempFolderStorage()
            sample_file_data = bytes()
            for chunk in sample_file.chunks():
                sample_file_data += chunk
            samples_tmp_storage.save(sample_file_data, 'wb')
            try:
                samples_tmp_storage.read('rb')
            except Exception as e:
                print(e)
            self.sample_files_dict[sample_file.name] = samples_tmp_storage.name

    def save_file_actions_dict(self):
        self.sample_files_dict['file_actions'] = self.file_actions_dict

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        if 'request' in kwargs:
            sample_files = kwargs.pop('request').FILES.getlist('sample_files')
            self.save_sample_files(sample_files)
            self.create_samples_dataset(kwargs.pop('data'))
            self.save_file_actions_dict()
        else:
            self.retrieve_stored_sample_files()

    def get_or_init_instance(self, instance_loader, row):
        """
        Either fetches an already existing instance or initializes a new one.
        """
        instance = self.get_instance(instance_loader, row)
        if instance:
            return instance, False
        else:
            return self.init_instance(row), True

    def import_row(self, row, instance_loader, using_transactions=True, dry_run=False, **kwargs):
        """
        Imports data from ``tablib.Dataset``. Refer to :doc:`import_workflow`
        for a more complete description of the whole import process.

        :param self: Originally "self" would be a TalentResource object.
            Optional methods: self.before_import_row(row, **kwargs),
            self.after_import_instance(instance, new, **kwargs),
            self.after_import_row(row, row_result, **kwargs)

        :param row: A ``dict`` of the row to import

        :param instance_loader: The instance loader to be used to load the row

        :param using_transactions: If ``using_transactions`` is set, a transaction
            is being used to wrap the import

        :param dry_run: If ``dry_run`` is set, or error occurs, transaction
            will be rolled back.
        """
        instance, new = self.get_or_init_instance(instance_loader, row)
        row_result = self.get_row_result_class()()
        new_file = row['audio_file']
        row_result.import_type = RowResult.IMPORT_TYPE_ERROR
        try:
            if new_file in self.file_actions_dict['skip_import']:
                row_result.import_type = RowResult.IMPORT_TYPE_SKIP
            elif new_file in self.file_actions_dict['duplicate']:
                row_result.import_type = RowResult.IMPORT_TYPE_DUPLICATE
            elif new_file in self.file_actions_dict['replace'].keys():
                row_result.import_type = RowResult.IMPORT_TYPE_REPLACE
            elif new_file in self.file_actions_dict['update_welo_id'].keys():
                row_result.import_type = RowResult.IMPORT_TYPE_UPDATE_WELO_ID
                row_result.update_talent = self.file_actions_dict['update_welo_id'][new_file]
            elif new_file in self.file_actions_dict['new'].keys():
                row_result.import_type = RowResult.IMPORT_TYPE_NEW
            elif not new:
                row_result.import_type = RowResult.IMPORT_TYPE_UPDATE

            row_result.new_record = new
            original = deepcopy(instance)
            diff = Diff(self, original, new)
            self.import_obj(instance, row, dry_run)
            with transaction.atomic():
                if dry_run:
                    self.save_instance(instance, using_transactions, dry_run)
                else:
                    if row_result.import_type == "new":
                        print("New: %s" % new_file)
                        instance.vendor = kwargs['user'].userprofile.vendor
                        instance.type = 'PRO'
                        instance.audio_file.save(os.path.basename(new_file),
                                                 ContentFile(self.retrieved_sample_files_dict[new_file]))
                        instance.audio_file_sha = self.file_actions_dict['new'][new_file]
                        instance.save()
                    elif row_result.import_type == "update_welo_id":
                        file_to_update = self.file_actions_dict['update_welo_id'][new_file]
                        print("Update file and welo_id: new file -- %s Welo ID -- %s" % (new_file, file_to_update))
                        talent_to_update = models.Talent.objects.filter(welo_id=file_to_update)[0]
                        old_path = talent_to_update.audio_file.path
                        if talent_to_update.vendor != kwargs['user'].userprofile.vendor:
                            talent_to_update.vendor = kwargs['user'].userprofile.vendor
                        talent_to_update.audio_file.save(os.path.basename(new_file),
                                                         ContentFile(self.retrieved_sample_files_dict[new_file]))
                        talent_to_update.audio_file_sha = talent_to_update.get_audio_file_sha()
                        if os.path.exists(old_path):
                            os.remove(old_path)
                        talent_to_update.save()
                    elif row_result.import_type == "duplicate":
                        print("Duplicate (pass): %s" % new_file)
                    elif row_result.import_type == "replace":
                        talent_to_update = self.file_actions_dict['replace'][new_file]
                        print("Replace: %s" % new_file)
                    elif row_result.import_type == "skip":
                        print("File not uploaded (pass): %s" % new_file)
            diff.compare_with(self, instance, dry_run)
            if row_result.update_talent:
                diff.right[0] = "%s (%s)" % (diff.right[0], row_result.update_talent)

            row_result.diff = diff.as_html()
            self.after_import_row(row, row_result, **kwargs)
        except Exception as e:
            # There is no point logging a transaction error for each row
            # when only the original error is likely to be relevant
            if not isinstance(e, TransactionManagementError):
                logging.exception(e)
            tb_info = traceback.format_exc()
            row_result.errors.append(self.get_error_result_class()(e, tb_info, row))
        return row_result

    code = fields.Field(
        column_name='code',
        attribute='language',
        widget=ForeignKeyWidget(models.Language, 'code')
    )

    class Meta:
        model = models.Talent
        skip_unchanged = True
        report_skipped = True
        fields = ('audio_file', 'gender', 'code')
        export_order = fields
        instance_loader_class = ModelInstanceLoaderWithSamples
        import_id_fields = ['audio_file']



