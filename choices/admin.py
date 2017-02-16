from django import forms
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.db import models as dbmodels
from django.shortcuts import render
from . import models, filters
from .forms import SelectClientForm, AudioFileAdminForm
from .samples_import import ImportExportActionWithSamples
from django.contrib import admin
from django.http import HttpResponseRedirect

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
                    AudioFileAdminForm.print_error(e)

            plural = ''
            if count != 1:
                plural = 's'

            self.message_user(request, "Successfully assigned %s talent%s to %s." % (count, plural, client.name))
            return HttpResponseRedirect('/admin/choices/selection/')

    if not form:
        form = SelectClientForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render(request, 'admin/add_selections.html', {'selections': queryset, 'client_form': form})

add_selection.short_description = "Create new selections"


class TalentAdmin(ImportExportActionWithSamples):
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
                    'created_at', 'updated_at', 'average_rating', 'get_times_preapproved', 'get_times_accepted',
                    'get_times_rejected')
    list_display_links = ('id', 'welo_id')
    readonly_fields = ('rate', 'welo_id', 'audio_file_sha', 'average_rating', 'created_at', 'updated_at')
    search_fields = ('id', 'welo_id', 'vendor__name', 'language__language')
    list_per_page = 100

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


class ReadOnlyModelAdmin(admin.ModelAdmin):
    actions = None
    list_display_links = None
    # more stuff here

    def has_add_permission(self, request):
        return False


class CommentAdmin(ReadOnlyModelAdmin):
    list_filter = (
        ('author', filters.FilteredRelatedOnlyFieldListFilter),
    )
    list_display = ('selection', 'author', 'text', 'comment_client', 'created_date')
    search_fields = ['text', 'author__user__username', 'author__client__username', 'selection__talent__welo_id']
admin.site.register(models.Comment, CommentAdmin)


class RatingAdmin(ReadOnlyModelAdmin):
    list_display = ('id', 'rating', 'talent', 'rater')
    list_filter = (
        ('rating', filters.FilteredAllValuesFieldListFilter),
        ('rater', filters.FilteredRelatedOnlyFieldListFilter)
    )
    search_fields = ('talent__welo_id',)
admin.site.register(models.Rating, RatingAdmin)
