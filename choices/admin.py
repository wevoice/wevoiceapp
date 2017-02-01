import os
from django import forms
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.db import models as dbmodels
from django.shortcuts import render
from import_export.admin import ImportExportActionModelAdmin
from . import models, filters, samples_import
from .forms import SelectClientForm, BaseAudioForm
import django
import json
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import pluralize
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from import_export.signals import post_import
from import_export.results import RowResult
from import_export.formats import base_formats


admin.site.site_title = 'Voiceover Admin'
admin.site.site_header = 'Voiceover Admin'
admin.site.register(Permission)


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


class TalentAdmin(ImportExportActionModelAdmin):
    form = AudioFileAdminForm
    actions = [add_selection]
    inlines = [RatingInline]

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
                    'average_rating', 'get_times_preapproved', 'get_times_accepted', 'get_times_rejected', 'created_at',
                    'updated_at')
    list_display_links = ('id', 'welo_id')
    readonly_fields = ('rate', 'welo_id', 'audio_file_sha', 'average_rating', 'created_at', 'updated_at')
    search_fields = ('id', 'welo_id', 'vendor__name', 'language__language')
    list_per_page = 100

    def get_import_formats(self):
        return [f for f in (base_formats.XLSX,) if f().can_import()]

    def get_export_formats(self):
        return [f for f in (base_formats.XLSX,) if f().can_import()]

    def save_model(self, request, obj, form, change):
        if not obj.audio_file_sha or 'audio_file' in form.changed_data:
            obj.audio_file_sha = form.current_file_sha(obj.audio_file.file)
        super(TalentAdmin, self).save_model(request, obj, form, change)

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


class VendorsTalentAdmin(TalentAdmin):
    resource_class = samples_import.TalentResource
    import_template_name = "multi_file_import.html"

    def get_queryset(self, request):
        qs = super(TalentAdmin, self).get_queryset(request)
        if request.user.userprofile.vendor:
            qs = qs.filter(vendor__name=request.user.userprofile.vendor.name)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vendor":
            kwargs["queryset"] = models.Vendor.objects.filter(username=request.user.userprofile.vendor.username)
        return super(VendorsTalentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_skip_admin_log(self):
        return True

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
        form = samples_import.ImportFormWithSamples(import_formats, request.POST or None, request.FILES or None)

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
                BaseAudioForm.print_error(e)
                # return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
            except Exception as e:
                BaseAudioForm.print_error(e)
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
                context['confirm_form'] = samples_import.ConfirmImportFormWithSamples(initial={
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format'],
                    'sample_files_dict': json.dumps(self.resource_class.sample_files_dict),
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
        return TemplateResponse(request, [self.import_template_name],
                                context)

    @method_decorator(require_POST)
    def process_import(self, request, *args, **kwargs):
        """
        Perform the actual import action (after the user has confirmed he
        wishes to import)
        """
        opts = self.model._meta
        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        confirm_form = samples_import.ConfirmImportFormWithSamples(request.POST)
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

            action_items = self.resource_class.file_actions_dict
            for key, value in action_items.items():
                if key in ['new', 'update_welo_id', 'replace']:
                    print(key + "|" + str(value))

            if not self.get_skip_admin_log():
                # Add imported objects to LogEntry
                logentry_map = {
                    RowResult.IMPORT_TYPE_NEW: ADDITION,
                    RowResult.IMPORT_TYPE_UPDATE: CHANGE,
                    RowResult.IMPORT_TYPE_DELETE: DELETION,
                }
                content_type_id = ContentType.objects.get_for_model(self.model).pk
                for row in result:
                    if row.import_type != row.IMPORT_TYPE_ERROR and row.import_type != row.IMPORT_TYPE_SKIP:
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=content_type_id,
                            object_id=row.object_id,
                            object_repr=row.object_repr,
                            action_flag=logentry_map[row.import_type],
                            change_message="%s through import_export" % row.import_type,
                        )

            success_message = u'Import finished, with {} new {}{} and ' \
                              u'{} updated {}{}.'.format(result.totals[RowResult.IMPORT_TYPE_NEW],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_NEW]),
                                                         result.totals[RowResult.IMPORT_TYPE_UPDATE],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_UPDATE]))

            success_message = u'Import finished'

            messages.success(request, success_message)
            tmp_storage.remove()

            post_import.send(sender=None, model=self.model)

            url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)
admin.site.register(models.TalentsByVendor, VendorsTalentAdmin)
