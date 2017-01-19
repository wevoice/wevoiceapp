import sys
import os
import hashlib
import django
import openpyxl
import tablib
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models as dbmodels
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.defaultfilters import pluralize
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.widgets import ForeignKeyWidget
from import_export.forms import ImportForm, ConfirmImportForm
from import_export import fields
from import_export.results import RowResult
from import_export.signals import post_import
from . import models, filters
from .forms import SelectClientForm
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import json
from django.utils.encoding import force_text

XLSX_IMPORT = True
admin.site.site_title = 'Voiceover Admin'
admin.site.site_header = 'Voiceover Admin'


class BaseAudioForm(forms.ModelForm):

    @staticmethod
    def print_error(e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)

    @classmethod
    def current_file_sha(cls, current_file):
        sha = hashlib.sha1()
        current_file.seek(0)
        try:
            data = None
            while True:
                chunk = current_file.read(65536)
                if chunk:
                    data = chunk
                else:
                    break
            sha.update(data)
            sha1 = sha.hexdigest()
            current_file.seek(0)
        except Exception as e:
            cls.print_error(e)
            return '0'
        else:
            return sha1


class AudioFilesForm(BaseAudioForm):
    audio_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def clean(self):
        cleaned_data = self.cleaned_data
        files = self.files.getlist('audio_files')
        if self.is_valid():
            for f in files:
                current_file_sha = self.current_file_sha(f)
                destination = settings.MEDIA_ROOT
                match_qs = models.Talent.objects.filter(audio_file_sha=current_file_sha)
                if match_qs.count() > 0:
                    if f.name == match_qs[0].audio_file.name:
                        print("Ignore: Content and name of %s is same as for talent %s" % (f.name, match_qs[0].welo_id))
                    elif f.name != match_qs[0].audio_file.name:
                        print("Change talent name: the content of %s is the same as %s" % (f.name, match_qs[0].welo_id))
                elif os.path.isfile(destination + f.name):
                    print('Overwrite old file with new: a file named %s with different content already exists' % f.name)
                else:
                    print('Add new talent: the file name and content is new for file %s' % f.name)
        return cleaned_data


class UploadAdmin(admin.ModelAdmin):
    form = AudioFilesForm
admin.site.register(models.Upload, UploadAdmin)


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    list_display = ('id', 'username', 'client_or_vendor_name', 'first_name', 'last_name', 'email', 'is_active',
                    'is_superuser')
    list_display_links = ('id', 'username')

    def client_or_vendor_name(self, obj):
        if obj.userprofile.client:
            return "Client: %s" % obj.userprofile.client.name
        elif obj.userprofile.vendor:
            return "Vendor: %s" % obj.userprofile.vendor.name
        elif obj.is_superuser:
            return "Administrator"

    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ClientAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_display = ('id', 'name', 'username')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 100
admin.site.register(models.Client, ClientAdmin)


class VendorAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_display = ('id', 'name', 'username')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 100
admin.site.register(models.Vendor, VendorAdmin)


class LanguageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_display = ('id', 'language')
    list_display_links = ('id', 'language')
    search_fields = ('language',)
    list_per_page = 100
admin.site.register(models.Language, LanguageAdmin)


class AudioFileAdminForm(BaseAudioForm):
    def clean_audio_file(self):
        if "audio_file" in self.changed_data:
            current_file = self.cleaned_data.get("audio_file")
            current_file_sha = self.current_file_sha(current_file)
            destination = settings.MEDIA_ROOT
            match_qs = models.Talent.objects.filter(audio_file_sha=current_file_sha)
            if match_qs.count() > 0:
                raise forms.ValidationError('This is the same content as the sample for talent ' + match_qs[0].welo_id)
            if os.path.isfile(destination + current_file.name):
                raise forms.ValidationError('A file named '
                                            + current_file.name +
                                            ' already exists. Please rename your file and try again.')
            else:
                return self.cleaned_data["audio_file"]


class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'rating', 'talent', 'rater')
    list_filter = (
        ('rating', filters.FilteredAllValuesFieldListFilter),
        ('rater', filters.FilteredRelatedOnlyFieldListFilter)
    )
    search_fields = ('talent__welo_id',)
admin.site.register(models.Rating, RatingAdmin)


class RatingInline(admin.StackedInline):
    model = models.Rating
    readonly_fields = ('rater', 'talent', 'rating')
    extra = 0


class ImportFormWithSamples(ImportForm):
    sample_files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}, ),
        label=_('Sample Files'),
        required=False
    )

    @staticmethod
    def selective_create_dataset(in_stream, sample_files_dict):
        """
        Create dataset from first sheet.
        """
        assert XLSX_IMPORT
        from io import BytesIO
        xlsx_book = openpyxl.load_workbook(BytesIO(in_stream), read_only=True)

        dataset = tablib.Dataset()
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

        messages_dict = {'not_in_uploads': {'message': messages_dict['1'],
                                            'action': actions_dict['1'],
                                            'file_pairs': []},
                         'same_name_content': {'message': messages_dict['2'],
                                               'action': actions_dict['1'],
                                               'file_pairs': []},
                         'same_name_diff_content': {'message': messages_dict['3'],
                                                    'action': actions_dict['2'],
                                                    'file_pairs': []},
                         'same_content_diff_name': {'message': messages_dict['4'],
                                                    'action': actions_dict['3'],
                                                    'file_pairs': []},
                         'new_name_new_content': {'message': messages_dict['5'],
                                                  'action': actions_dict['4'],
                                                  'file_pairs': []}}

        rows = sheet.rows
        dataset.headers = [cell.value for cell in next(rows)]

        import_file = True
        if 'prerun' not in sample_files_dict:

            sample_files_dict['prerun'] = True

            for row in rows:
                existing_talent = models.Talent.objects.filter(audio_file=row[1].value.replace(" ", "_"))
                import_file_sha = None
                talent_with_matching_file_sha = None
                if row[1].value in sample_files_dict:
                    import_file_sha = BaseAudioForm.current_file_sha(File(open(sample_files_dict[row[1].value])))
                    talent_with_matching_file_sha = models.Talent.objects.filter(audio_file_sha=import_file_sha)
                else:
                    upload_file = row[1].value
                    import_file = False
                    messages_dict['not_in_uploads']['file_pairs'].append(upload_file)
                    print("%s: %s | %s" % (upload_file, messages_dict['not_in_uploads']['message'],
                                           messages_dict['not_in_uploads']['action']))
                if existing_talent.exists():
                    if import_file_sha and import_file_sha == existing_talent[0].audio_file_sha:
                        file_pair = (existing_talent[0].welo_id, row[1].value)
                        import_file = False
                        sample_files_dict.pop(row[1].value, None)
                        messages_dict['same_name_content']['file_pairs'].append(file_pair)
                        print("%s: %s | %s" % (str(file_pair), messages_dict['same_name_content']['message'],
                                               messages_dict['same_name_content']['action']))
                    else:
                        file_pair = (existing_talent[0].welo_id, row[1].value)
                        import_file = False
                        sample_files_dict.pop(row[1].value, None)
                        messages_dict['same_name_diff_content']['file_pairs'].append(file_pair)
                        print("%s: %s | %s" % (str(file_pair), messages_dict['same_name_diff_content']['message'],
                                               messages_dict['same_name_diff_content']['action']))
                elif talent_with_matching_file_sha and talent_with_matching_file_sha.exists():
                    file_pair = (talent_with_matching_file_sha[0].welo_id, row[1].value)
                    import_file = False
                    sample_files_dict.pop(row[1].value, None)
                    messages_dict['same_content_diff_name']['file_pairs'].append(file_pair)
                    print("%s: %s | %s" % (str(file_pair), messages_dict['same_content_diff_name']['message'],
                                           messages_dict['same_content_diff_name']['action']))
                if import_file:
                    upload_file = row[1].value
                    messages_dict['new_name_new_content']['file_pairs'].append(upload_file)
                    print("%s: %s | %s" % (upload_file, messages_dict['new_name_new_content']['message'],
                                           messages_dict['new_name_new_content']['action']))
                    row_values = [cell.value for cell in row]
                    dataset.append(row_values)
        else:
            for row in rows:
                if row[1].value in sample_files_dict:
                    row_values = [cell.value for cell in row]
                    dataset.append(row_values)
        return dataset


class ConfirmImportFormWithSamples(ConfirmImportForm):
    sample_files_dict = forms.CharField(widget=forms.HiddenInput())

    def clean_sample_files_dict(self):
        return json.loads(self.cleaned_data['sample_files_dict'])


class TalentResource(resources.ModelResource):
    vendor_name = fields.Field(
        column_name='vendor',
        attribute='vendor',
        widget=ForeignKeyWidget(models.Vendor, 'name')
    )

    code = fields.Field(
        column_name='code',
        attribute='language',
        widget=ForeignKeyWidget(models.Language, 'code')
    )

    class Meta:
        model = models.Talent
        skip_unchanged = True
        report_skipped = False
        fields = ('id', 'audio_file', 'vendor_name', 'type', 'gender', 'age_range', 'code')
        export_order = fields


def add_selection(self, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = SelectClientForm(request.POST)

        if form.is_valid():
            client = models.Client.objects.get(name=form.cleaned_data['client'])
            count = 0
            for qs in queryset:
                if queryset.model._meta.model_name == 'talent':
                    talent = qs
                else:
                    talent = qs.talent
                try:
                    new_selection, created = models.Selection.objects.get_or_create(
                        talent=talent,
                        client=client
                    )
                    if created:
                        new_selection.save()
                        count += 1
                except Exception as e:
                    BaseAudioForm.print_error(e)

            plural = ''
            if count != 1:
                plural = 's'

            self.message_user(request, "Successfully assigned %s talent%s to %s." % (count, plural, client.name))
            return HttpResponseRedirect('/admin/choices/selection/')

    if not form:
        form = SelectClientForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render(request, 'admin/add_selections.html', {'selections': queryset, 'client_form': form})

add_selection.short_description = "Create new selections"


def delete_talents(self, request, queryset):
    for talent in queryset:
        talent.delete()
    self.message_user(request, "Successfully deleted %s talents." % queryset.count())
    return HttpResponseRedirect('/admin/choices/talent/')
delete_talents.short_description = "Delete Talents"


class ImportExportWithSamplesActionModelAdmin(ImportExportActionModelAdmin):
    def save_sample_files(self, sample_files):
        sample_files_dict = {}
        for sample_file in sample_files:
            samples_tmp_storage = self.get_tmp_storage_class()()
            sample_file_data = bytes()
            for chunk in sample_file.chunks():
                sample_file_data += chunk
            samples_tmp_storage.save(sample_file_data, 'wb')
            try:
                samples_tmp_storage.read('rb')
            except Exception as e:
                print(e)
            sample_files_dict[sample_file.name] = samples_tmp_storage.name
        return sample_files_dict

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
        sample_files = request.FILES.getlist('sample_files')

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
            sample_files_dict = self.save_sample_files(sample_files)

            # then read the file, using the proper format-specific mode
            # warning, big files may exceed memory
            try:
                data = tmp_storage.read(input_format.get_read_mode())
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = form.selective_create_dataset(data, sample_files_dict)
            except UnicodeDecodeError as e:
                BaseAudioForm.print_error(e)
                # return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
            except Exception as e:
                BaseAudioForm.print_error(e)
                # return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__,
                #                                                                                   import_file.name)))

            result = resource.import_data(dataset, dry_run=True,
                                          raise_errors=False,
                                          file_name=import_file.name,
                                          user=request.user)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportFormWithSamples(initial={
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format'],
                    'sample_files_dict': json.dumps(sample_files_dict)
                })

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        context['title'] = _("Import")
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, ["multi_file_import.html"],
                                context)

    def retrieve_stored_sample_files(self, sample_files_dict):
        retrieved_sample_files_dict = {}
        for key, value in sample_files_dict.items():
            if key != 'prerun':
                retrieved_sample_file = self.get_tmp_storage_class()(name=value)
                data = retrieved_sample_file.read('rb')
                retrieved_sample_files_dict[key] = data
        return retrieved_sample_files_dict

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
            sample_files_dict = confirm_form.cleaned_data['sample_files_dict']
            stored_sample_files_dict = self.retrieve_stored_sample_files(sample_files_dict)
            dataset = ImportFormWithSamples.selective_create_dataset(data, sample_files_dict)
            result = resource.import_data(dataset, dry_run=False,
                                          raise_errors=True,
                                          file_name=confirm_form.cleaned_data['original_file_name'],
                                          user=request.user)

            if not self.get_skip_admin_log():
                # Add imported objects to LogEntry
                logentry_map = {
                    RowResult.IMPORT_TYPE_NEW: ADDITION,
                    RowResult.IMPORT_TYPE_UPDATE: CHANGE,
                    RowResult.IMPORT_TYPE_DELETE: DELETION,
                }
                content_type_id = ContentType.objects.get_for_model(self.model).pk
                counter = 0
                for row in result:
                    if row.import_type != row.IMPORT_TYPE_ERROR and row.import_type != row.IMPORT_TYPE_SKIP:
                        if row.import_type == 'new':
                            filename = dataset._data[counter]._row[1]
                            new_talent = models.Talent.objects.filter(audio_file=filename)
                            if new_talent > 0:
                                if filename in stored_sample_files_dict:
                                    new_talent[0].audio_file.save(os.path.basename(filename),
                                                                  ContentFile(stored_sample_files_dict[filename]))
                                    new_talent[0].save()
                                else:
                                    new_talent.delete()
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=content_type_id,
                            object_id=row.object_id,
                            object_repr=row.object_repr,
                            action_flag=logentry_map[row.import_type],
                            change_message="%s through import_export" % row.import_type,
                        )
                    counter += 1

            success_message = u'Import finished, with {} new {}{} and ' \
                              u'{} updated {}{}.'.format(result.totals[RowResult.IMPORT_TYPE_NEW],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_NEW]),
                                                         result.totals[RowResult.IMPORT_TYPE_UPDATE],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_UPDATE]))

            messages.success(request, success_message)
            tmp_storage.remove()

            post_import.send(sender=None, model=self.model)

            url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)


class TalentAdmin(ImportExportWithSamplesActionModelAdmin):
    form = AudioFileAdminForm
    actions = [add_selection, delete_talents]
    inlines = [RatingInline]
    resource_class = TalentResource

    def get_queryset(self, request):
        qs = super(TalentAdmin, self).get_queryset(request)
        if request.user.userprofile.vendor:
            qs = qs.filter(vendor__name=request.user.userprofile.vendor.name)
        return qs

    formfield_overrides = {
        dbmodels.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_filter = (('gender', filters.FilteredChoicesFieldListFilter),
                   ('type', filters.FilteredChoicesFieldListFilter),
                   ('age_range', filters.FilteredChoicesFieldListFilter),
                   ('average_rating', filters.FilteredAllValuesFieldListFilter),
                   filters.InReviewFilter,
                   filters.PreapprovedFilter,
                   filters.ApprovedFilter,
                   filters.RejectedFilter,
                   ('vendor', filters.FilteredRelatedOnlyFieldListFilter),
                   ('language', filters.FilteredRelatedOnlyFieldListFilter))
    list_display = ('id', 'welo_id', 'vendor', 'audio_file_player', 'language', 'type', 'gender', 'age_range',
                    'average_rating', 'get_times_preapproved', 'get_times_accepted', 'get_times_rejected')
    list_display_links = ('id', 'welo_id')
    readonly_fields = ('rate', 'welo_id')
    search_fields = ('welo_id', 'vendor__name', 'language__language')
    list_per_page = 100

    def get_actions(self, request):
        actions = super(TalentAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    class Media:
        def __init__(self):
            pass

        js = (
            'jquery/jquery-1.4.min.js',
            'jquery/jquery.simpleplayer.min.js',
            'js/admin/extra-admin.js',
        )
        css = {
             'all': ('css/admin/extra-admin.css',)
        }
admin.site.register(models.Talent, TalentAdmin)


class CommentInline(admin.StackedInline):
    model = models.Comment
    readonly_fields = ('selection', 'author', 'text', 'created_date')
    extra = 0


class SelectionAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    actions = [add_selection, ]
    list_filter = (
        ('status', filters.FilteredChoicesFieldListFilter),
        ('talent__gender', filters.FilteredChoicesFieldListFilter),
        filters.CommentsCountFilter,
        ('talent__average_rating', filters.FilteredAllValuesFieldListFilter),
        ('client', filters.FilteredRelatedOnlyFieldListFilter),
        ('talent__vendor', filters.FilteredRelatedOnlyFieldListFilter),
        ('talent__language', filters.FilteredRelatedOnlyFieldListFilter)
    )
    list_display = ('id', 'talent', 'client', 'status', 'audio_file_player', 'talent_language',
                    'talent_gender', 'talent_vendor', 'talent_age_range', 'talent_average_rating', 'total_comments')
    search_fields = ['client__username', 'client__name', 'talent__welo_id', 'talent__vendor__name']

    class Media:
        def __init__(self):
            pass

        js = (
            'jquery/jquery-1.4.min.js',
            'jquery/jquery.simpleplayer.min.js',
            'js/admin/extra-admin.js',
        )
        css = {
             'all': ('css/admin/extra-admin.css',)
        }
admin.site.register(models.Selection, SelectionAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_filter = (
        ('author', filters.FilteredRelatedOnlyFieldListFilter),
    )
    list_display = ('selection', 'author', 'text', 'comment_client', 'created_date')
    search_fields = ['text', 'author__user__username', 'author__client__username', 'selection__talent__welo_id']
admin.site.register(models.Comment, CommentAdmin)
