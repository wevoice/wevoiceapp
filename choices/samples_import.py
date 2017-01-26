import json
import openpyxl
import tablib
import traceback
from collections import OrderedDict
from copy import deepcopy
from django import forms
from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.db.transaction import TransactionManagementError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
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

USE_TRANSACTIONS = getattr(settings, 'IMPORT_EXPORT_USE_TRANSACTIONS', True)

XLSX_IMPORT = True


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

RowResult.IMPORT_TYPE_DUPLICATE = 'duplicate'
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
                               (RowResult.IMPORT_TYPE_DELETE, 0),
                               (RowResult.IMPORT_TYPE_SKIP, 0),
                               (RowResult.IMPORT_TYPE_DUPLICATE, 0),
                               (RowResult.IMPORT_TYPE_ERROR, 0)])
    self.total_rows = 0

Result.__init__ = new_result_init


class TalentResource(resources.ModelResource):
    sample_files_dict = {}
    dataset_with_samples = None
    template_messages_dict = {}
    retrieved_sample_files_dict = {}

    def create_samples_dataset(self, in_stream):
        """
        Create dataset_with_samples from first sheet.
        """
        assert XLSX_IMPORT
        from io import BytesIO
        xlsx_book = openpyxl.load_workbook(BytesIO(in_stream), read_only=True)

        dataset_with_samples = tablib.Dataset()
        sheet = xlsx_book.active

        actions_dict = {'1': 'Did not import',
                        '2': 'Replaced the talent file with the uploaded file',
                        '3': 'Renamed the talent and its file with the uploaded file name',
                        '4': 'Created new talent'}

        messages_dict = {'1': 'No matching filename in the uploaded fileset',
                         '2': 'Talent exists with same name and content as file',
                         '3': 'Talent exists with same name but different content as file',
                         '4': 'Talent exists same content but different name as file',
                         '5': 'No existing talent with this name or content'}

        template_messages_dict = {'not_in_uploads': {'message': messages_dict['1'], 'action': actions_dict['1'],
                                                     'file_pairs': []},
                                  'same_name_content': {'message': messages_dict['2'], 'action': actions_dict['1'],
                                                        'file_pairs': []},
                                  'same_name_diff_content': {'message': messages_dict['3'], 'action': actions_dict['2'],
                                                             'file_pairs': []},
                                  'same_content_diff_name': {'message': messages_dict['4'], 'action': actions_dict['3'],
                                                             'file_pairs': []},
                                  'new_name_new_content': {'message': messages_dict['5'], 'action': actions_dict['4'],
                                                           'file_pairs': []}}

        rows = sheet.rows
        dataset_with_samples.headers = [cell.value for cell in next(rows)]

        import_file = True
        for row in rows:
            existing_talent = models.Talent.objects.filter(audio_file=row[0].value.replace(" ", "_"))
            import_file_sha = None
            talent_with_matching_file_sha = None
            if row[0].value in self.sample_files_dict:
                import_file_sha = BaseAudioForm.current_file_sha(File(open(self.sample_files_dict[row[0].value])))
                talent_with_matching_file_sha = models.Talent.objects.filter(audio_file_sha=import_file_sha)
            else:
                upload_file = row[0].value
                import_file = False
                template_messages_dict['not_in_uploads']['file_pairs'].append(upload_file)
            if existing_talent.exists():
                if import_file_sha and import_file_sha == existing_talent[0].audio_file_sha:
                    file_pair = (existing_talent[0].welo_id, row[0].value)
                    import_file = False
                    self.sample_files_dict.pop(row[0].value, None)
                    template_messages_dict['same_name_content']['file_pairs'].append(file_pair)
                else:
                    file_pair = (existing_talent[0].welo_id, row[0].value)
                    import_file = False
                    self.sample_files_dict.pop(row[0].value, None)
                    template_messages_dict['same_name_diff_content']['file_pairs'].append(file_pair)
            elif talent_with_matching_file_sha and talent_with_matching_file_sha.exists():
                file_pair = (talent_with_matching_file_sha[0].welo_id, row[0].value)
                import_file = False
                self.sample_files_dict.pop(row[0].value, None)
                template_messages_dict['same_content_diff_name']['file_pairs'].append(file_pair)
            if import_file:
                upload_file = row[0].value
                template_messages_dict['new_name_new_content']['file_pairs'].append(upload_file)
                row_values = [cell.value for cell in row]
                dataset_with_samples.append(row_values)
        for key, value in template_messages_dict.iteritems():
            if len(value['file_pairs']) > 0:
                print("%s | %s" % (value['message'], value['action']))
                for pair in value['file_pairs']:
                    # Perform updates here, based on action type
                    print(str(pair))
        return dataset_with_samples, template_messages_dict

    def retrieve_stored_sample_files(self):
        self.retrieved_sample_files_dict = {}
        for key, value in self.sample_files_dict.items():
            if key != 'prerun':
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

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        if 'request' in kwargs:
            sample_files = kwargs.pop('request').FILES.getlist('sample_files')
            self.save_sample_files(sample_files)
            self.dataset_with_samples, self.template_messages_dict = self.create_samples_dataset(kwargs.pop('data'))
        else:
            self.retrieve_stored_sample_files()

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
        row_result = self.get_row_result_class()()
        new_file = row['audio_file']
        m_dict = self.template_messages_dict
        row_result.import_type = RowResult.IMPORT_TYPE_ERROR
        try:
            self.before_import_row(row, **kwargs)
            instance, new = self.get_or_init_instance(instance_loader, row)
            self.after_import_instance(instance, new, **kwargs)
            if new and new_file in self.sample_files_dict:
                row_result.import_type = RowResult.IMPORT_TYPE_NEW
            elif new_file in m_dict['not_in_uploads']['file_pairs']:
                row_result.import_type = RowResult.IMPORT_TYPE_SKIP
            elif new_file in [i for s in m_dict['same_name_content']['file_pairs'] for i in s]:
                row_result.import_type = RowResult.IMPORT_TYPE_DUPLICATE
            elif new_file in [i for s in m_dict['same_content_diff_name']['file_pairs'] for i in s]:
                row_result.import_type = RowResult.IMPORT_TYPE_UPDATE
            elif new_file in [i for s in m_dict['same_name_diff_content']['file_pairs'] for i in s]:
                row_result.import_type = RowResult.IMPORT_TYPE_DELETE
            else:
                row_result.import_type = RowResult.IMPORT_TYPE_ERROR

            row_result.new_record = new
            original = deepcopy(instance)
            diff = Diff(self, original, new)
            if self.for_delete(row, instance):
                if new:
                    row_result.import_type = RowResult.IMPORT_TYPE_SKIP
                    diff.compare_with(self, None, dry_run)
                else:
                    row_result.import_type = RowResult.IMPORT_TYPE_DELETE
                    self.delete_instance(instance, using_transactions, dry_run)
                    diff.compare_with(self, None, dry_run)
            else:
                self.import_obj(instance, row, dry_run)
                if self.skip_row(instance, original):
                    row_result.import_type = RowResult.IMPORT_TYPE_SKIP
                else:
                    with transaction.atomic():
                        self.save_instance(instance, using_transactions, dry_run)
                    self.save_m2m(instance, row, using_transactions, dry_run)
                diff.compare_with(self, instance, dry_run)
            row_result.diff = diff.as_html()
            # Add object info to RowResult for LogEntry
            if row_result.import_type != RowResult.IMPORT_TYPE_SKIP:
                row_result.object_id = instance.pk
                row_result.object_repr = force_text(instance)
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
