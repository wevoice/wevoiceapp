import openpyxl
import os
import traceback
import django
import json
from collections import OrderedDict
from copy import deepcopy
from django import forms
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.transaction import TransactionManagementError
from import_export import fields
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.formats.base_formats import XLSX
from import_export.signals import post_import
from import_export.resources import Diff
from import_export.results import Result, RowResult
from import_export.widgets import ForeignKeyWidget
from import_export.forms import ImportForm, ConfirmImportForm
from import_export.tmp_storages import TempFolderStorage
from tablib import Dataset
from . import models
from .forms import AudioFileAdminForm


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
        label='Sample Files',
        required=False
    )


class ConfirmImportFormWithSamples(ConfirmImportForm):
    sample_files_dict = forms.CharField(widget=forms.HiddenInput())

    def clean_sample_files_dict(self):
        return json.loads(self.cleaned_data['sample_files_dict'])


def new_row_result_init(self):
    self.errors = []
    self.diff = None
    self.talent_obj = None
    self.import_type = None
    self.update_talent = None
    self.replace_talent = None

RowResult.IMPORT_TYPE_DUPLICATE = 'duplicate'
RowResult.IMPORT_TYPE_REPLACE = 'replace'
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
                               (RowResult.IMPORT_TYPE_REPLACE, 0),
                               (RowResult.IMPORT_TYPE_ERROR, 0)])
    self.total_rows = 0

Result.__init__ = new_result_init


class TalentResource(resources.ModelResource):
    sample_files_dict = {}
    file_actions_dict = {'skip': [], 'duplicate': [], 'replace': {}, 'update': {}, 'new': {}}
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
                self.file_actions_dict['skip'].append(row[0].value)
            else:
                existing_talent = models.Talent.objects.filter(audio_file=row[0].value)
                import_file_sha = AudioFileAdminForm.current_file_sha(File(open(self.sample_files_dict[row[0].value])))
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
                    self.file_actions_dict['update'][row[0].value] = t_with_matching_file_sha[0].welo_id
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

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        if 'request' in kwargs:
            sample_files = kwargs.pop('request').FILES.getlist('sample_files')
            self.save_sample_files(sample_files)
            self.create_samples_dataset(kwargs.pop('data'))
        else:
            self.retrieve_stored_sample_files()

    def import_row(self, row, instance_loader, using_transactions=True, dry_run=False, **kwargs):
        """
        Refer to parent class for usages
        """
        instance, new = self.get_or_init_instance(instance_loader, row)
        row_result = self.get_row_result_class()()
        new_file = row['audio_file']
        row_result.import_type = RowResult.IMPORT_TYPE_ERROR
        try:
            if new_file in self.file_actions_dict['skip']:
                row_result.import_type = RowResult.IMPORT_TYPE_SKIP
            elif new_file in self.file_actions_dict['duplicate']:
                row_result.import_type = RowResult.IMPORT_TYPE_DUPLICATE
            elif new_file in self.file_actions_dict['replace'].keys():
                row_result.import_type = RowResult.IMPORT_TYPE_REPLACE
            elif new_file in self.file_actions_dict['update'].keys():
                row_result.import_type = RowResult.IMPORT_TYPE_UPDATE
                row_result.update_talent = self.file_actions_dict['update'][new_file]
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
                        instance.vendor = kwargs['user'].userprofile.vendor
                        instance.type = 'PRO'
                        instance.audio_file.save(os.path.basename(new_file),
                                                 ContentFile(self.retrieved_sample_files_dict[new_file]))
                        instance.audio_file_sha = self.file_actions_dict['new'][new_file]
                        instance.save()
                    elif row_result.import_type == "update":
                        file_to_update = self.file_actions_dict['update'][new_file]
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
                        pass
                    elif row_result.import_type == "replace":
                        talent_to_replace = self.file_actions_dict['replace'][new_file]
                        talent_to_replace = models.Talent.objects.filter(welo_id=talent_to_replace)[0]
                        if talent_to_replace.vendor != kwargs['user'].userprofile.vendor:
                            talent_to_replace.vendor = kwargs['user'].userprofile.vendor
                        old_path = talent_to_replace.audio_file.path
                        if os.path.exists(old_path):
                            os.remove(old_path)
                        talent_to_replace.audio_file.save(os.path.basename(new_file),
                                                          ContentFile(self.retrieved_sample_files_dict[new_file]))
                        talent_to_replace.audio_file_sha = talent_to_replace.get_audio_file_sha()
                        talent_to_replace.save()
                    elif row_result.import_type == "skip":
                        pass
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
        import_id_fields = ['audio_file']


class ImportExportActionWithSamples(ImportExportActionModelAdmin):
    resource_class = TalentResource
    import_template_name = "multi_file_import.html"
    change_list_template = "change_list_selective_import.html"
    formats = (XLSX,)

    def get_queryset(self, request):
        qs = super(ImportExportActionWithSamples, self).get_queryset(request)
        if request.user.userprofile.vendor:
            qs = qs.filter(vendor__name=request.user.userprofile.vendor.name)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vendor":
            kwargs["queryset"] = models.Vendor.objects.filter(username=request.user.userprofile.vendor.username)
        return super(ImportExportActionWithSamples, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def import_action(self, request, *args, **kwargs):
        """
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        """
        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        context = {}
        dataset = None

        import_formats = self.get_import_formats()
        form = ImportFormWithSamples(import_formats, request.POST or None, request.FILES or None)

        if request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            tmp_storage = self.get_tmp_storage_class()()
            data = bytes()
            for chunk in import_file.chunks():
                data += chunk

            tmp_storage.save(data, input_format.get_read_mode())

            # then read the file, using the proper format-specific mode
            # warning, big files may exceed memory
            try:
                data = tmp_storage.read(input_format.get_read_mode())
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
            except UnicodeDecodeError as e:
                AudioFileAdminForm.print_error(e)
                # return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
            except Exception as e:
                AudioFileAdminForm.print_error(e)
                # return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__,
                #                                                                                   import_file.name)))

            # Pass request and data here so that they can be used later
            result = resource.import_data(dataset,
                                          request=request,
                                          data=data,
                                          dry_run=True,
                                          raise_errors=False,
                                          use_transactions=False,
                                          # raise_errors=True,
                                          collect_failed_rows=False,
                                          file_name=import_file.name,
                                          user=request.user)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportFormWithSamples(initial={
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format'],
                    'sample_files_dict': json.dumps(self.resource_class.sample_files_dict),
                })

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        context['title'] = "Import"
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name],
                                context)

    def get_success_message(self, result, opts):
        success_message = 'The following results were processed for %s: ' % opts.model_name
        for key in result.totals:
            if result.totals[key] > 0:
                success_message += "%s -- %s; " % (key, result.totals[key])
        return success_message

    @method_decorator(require_POST)
    def process_import(self, request, *args, **kwargs):
        """
        Perform the actual import action (after the user has confirmed he
        wishes to import)
        """
        opts = self.model._meta
        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        confirm_form = ConfirmImportFormWithSamples(request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            tmp_storage = self.get_tmp_storage_class()(name=confirm_form.cleaned_data['import_file_name'])
            data = tmp_storage.read(input_format.get_read_mode())
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            result = resource.import_data(dataset, dry_run=False,
                                          raise_errors=True,
                                          file_name=confirm_form.cleaned_data['original_file_name'],
                                          user=request.user)

            messages.success(request, self.get_success_message(result, opts))
            tmp_storage.remove()

            post_import.send(sender=None, model=self.model)

            url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)
