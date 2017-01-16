import sys
import os
import hashlib
from django.contrib import admin
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.db import models as dbmodels
from django.shortcuts import render
from django.http import HttpResponseRedirect
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields
from . import models, filters
from .forms import SelectClientForm


def print_error(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(e, exc_type, fname, exc_tb.tb_lineno)


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


class AudioFileAdminForm(forms.ModelForm):
    def current_file_sha(self, current_file):
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
        except Exception as file_error:
            self.print_error(file_error)
            return '0'
        else:
            return sha1

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)

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


class TalentResource(resources.ModelResource):
    vendor_name = fields.Field(
        column_name='vendor',
        attribute='vendor',
        widget=ForeignKeyWidget(models.Vendor, 'name')
    )

    language_name = fields.Field(
        column_name='language',
        attribute='language',
        widget=ForeignKeyWidget(models.Language, 'language')
    )

    class Meta:
        model = models.Talent
        skip_unchanged = True
        report_skipped = False
        fields = ('id', 'welo_id', 'vendor_name', 'gender', 'age_range', 'language_name', 'audio_file')
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
                    print_error(e)
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
    actions = [add_selection, ]
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

    # def save_model(self, request, obj, form, change):
    #     current_file_sha = form.current_file_sha(obj.audio_file)
    #     obj.audio_file_sha = current_file_sha
    #     match_qs = models.Talent.objects.filter(file_sha1=current_file_sha)
    #     if match_qs.count() > 0:
    #         match_qs[0].audio_file = obj.audio_file.name
    #         match_qs[0].welo_id = obj.audio_file.name.split('.')[-1]
    #         # obj.file = match_qs[0].file
    #     else:
    #         obj.save()

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


admin.site.site_title = 'Voiceover Admin'
admin.site.site_header = 'Voiceover Admin'
