from django.contrib import admin
from . import models, filters
from django import forms
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.forms import Textarea
from django.db import models as dbmodels


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'is_active', 'is_superuser', 'email')
    list_display_links = ('id', 'username')

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
        dbmodels.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_display = ('id', 'name', 'username')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 100
admin.site.register(models.Client, ClientAdmin)


class VendorAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_display = ('id', 'name', 'username')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 100
admin.site.register(models.Vendor, VendorAdmin)


class LanguageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_display = ('id', 'language')
    list_display_links = ('id', 'language')
    search_fields = ('language',)
    list_per_page = 100
admin.site.register(models.Language, LanguageAdmin)


class AudioFileAdminForm(forms.ModelForm):
    def clean_audio_file(self):
        if "audio_file" in self.changed_data:
            current_file = self.cleaned_data.get("audio_file", False)
            destination = settings.MEDIA_ROOT
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


class TalentAdmin(admin.ModelAdmin):
    form = AudioFileAdminForm
    inlines = [RatingInline]

    def get_queryset(self, request):
        qs = super(TalentAdmin, self).get_queryset(request)
        if request.user.userprofile.vendor:
            qs = qs.filter(vendor__name=request.user.userprofile.vendor.name)
        return qs

    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 50})},
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
        # ('author__userprofile__client', admin.RelatedOnlyFieldListFilter),
    )
    list_display = ('selection', 'author', 'text', 'comment_client', 'created_date')
    search_fields = ['text', 'author__user__username', 'author__client__username', 'selection__talent__welo_id']
admin.site.register(models.Comment, CommentAdmin)


admin.site.site_title = 'WeVoice Admin'
admin.site.site_header = 'WeVoice Admin'
