from django.contrib import admin
from . import models
from django import forms
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.forms import Textarea
from django.db import models as dbmodels
from django.db.models import Count, Max, Avg


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'is_active', 'is_superuser', 'email')

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
    list_filter = ('rating', ('rater', admin.RelatedOnlyFieldListFilter))
    search_fields = ('talent__welo_id',)
admin.site.register(models.Rating, RatingAdmin)


class RejectedFilter(admin.SimpleListFilter):
    title = 'Times Rejected'
    parameter_name = 'rejected'

    def lookups(self, request, model_admin):
        rejected = model_admin.model.objects.filter(selection__status="REJECTED").annotate(num_rejected=Count('pk'))
        max_rejected = rejected.aggregate(max=Max('num_rejected'))

        tuple_set = ()
        for number in range(1, max_rejected['max'] + 1):
            tuple_set += ((number, str(number)),)

        return tuple_set

    def queryset(self, request, queryset):
        if self.value():
            rejected = queryset.filter(selection__status="REJECTED").annotate(num_rejected=Count('pk'))
            qs = rejected.filter(num_rejected__gte=self.value())
            return qs
        else:
            return queryset


class ApprovedFilter(admin.SimpleListFilter):
    title = 'Times Approved'
    parameter_name = 'approved'

    def lookups(self, request, model_admin):
        approved = model_admin.model.objects.filter(selection__status="APPROVED").annotate(num_approved=Count('pk'))
        max_approved = approved.aggregate(max=Max('num_approved'))
        tuple_set = ()
        for number in range(1, max_approved['max'] + 1):
            tuple_set += ((number, str(number)),)

        return tuple_set

    def queryset(self, request, queryset):
        if self.value():
            approved = queryset.filter(selection__status="APPROVED").annotate(num_approved=Count('pk'))
            qs = approved.filter(num_approved__gte=self.value())
            return qs
        else:
            return queryset


class TalentAdmin(admin.ModelAdmin):
    form = AudioFileAdminForm

    def get_queryset(self, request):
        qs = super(TalentAdmin, self).get_queryset(request)
        if request.user.userprofile.vendor:
            qs = qs.filter(vendor__name=request.user.userprofile.vendor.name)
        return qs

    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 50})},
    }
    list_filter = ('gender',
                   'type',
                   'age_range',
                   'average_rating',
                   RejectedFilter,
                   ApprovedFilter,
                   'vendor',
                   ('language', admin.RelatedOnlyFieldListFilter))
    list_display = ('id', 'welo_id', 'vendor', 'audio_file_player', 'language', 'type', 'gender', 'age_range',
                    'average_rating', 'get_times_accepted', 'get_times_rejected')
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
    readonly_fields = ('selection','author','text','created_date')
    extra = 0


class CommentsCountFilter(admin.SimpleListFilter):
    parameter_name = 'is_commented'
    title = 'Has Comments'
    YES, NO = 1, 0
    THRESHOLD = 1

    def lookups(self, request, model_admin):
        return (
            (self.YES, 'yes'),
            (self.NO, 'no'),
        )

    def queryset(self, request, queryset):
        qs = queryset.annotate(Count('comments'))

        if self.value() and int(self.value()) == self.YES:
            return qs.filter(comments__count__gte=self.THRESHOLD)
        if self.value() and int(self.value()) == self.NO:
            return qs.filter(comments__count__lt=self.THRESHOLD)

        return queryset


class SelectionAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    list_filter = ('status',
                   'talent__gender',
                   CommentsCountFilter,
                   'talent__average_rating',
                   ('client', admin.RelatedOnlyFieldListFilter),
                   ('talent__vendor', admin.RelatedOnlyFieldListFilter),
                   ('talent__language', admin.RelatedOnlyFieldListFilter)
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
    list_filter = (('selection__client', admin.RelatedOnlyFieldListFilter),
                   ('author', admin.RelatedOnlyFieldListFilter)
                   )
    list_display = ('selection', 'author', 'text', 'comment_client', 'created_date')
    search_fields = ['text', 'author__user__username', 'author__client__username', 'selection__talent__welo_id']
admin.site.register(models.Comment, CommentAdmin)


admin.site.site_title = 'WeVoice Admin'
admin.site.site_header = 'WeVoice Admin'
