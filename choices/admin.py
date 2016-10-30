from django.contrib import admin
from . import models
from django import forms
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.forms import Textarea
from django.db import models as dbmodels
from django.db.models import Count, Q
from choices.models import Talent


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


class InReviewFilter(admin.SimpleListFilter):
    parameter_name = 'under_review'
    title = 'in review'
    YES, NO = 1, 0

    def lookups(self, request, model_admin):
        return (
            (self.YES, 'yes'),
            (self.NO, 'no'),
        )

    def queryset(self, request, queryset):
        if self.value() and int(self.value()) == self.YES:
            return queryset.filter(
                Q(selection__status="REJECTED") |
                Q(selection__status="APPROVED") |
                Q(selection__status="PREAPPROVED")
            ).distinct()
        if self.value() and int(self.value()) == self.NO:
            return queryset.exclude(
                Q(selection__status="REJECTED") |
                Q(selection__status="APPROVED") |
                Q(selection__status="PREAPPROVED")
            ).distinct()
        return queryset


class RatingInline(admin.StackedInline):
    model = models.Rating
    readonly_fields = ('rater', 'talent', 'rating')
    extra = 0


class StatusFilter(admin.SimpleListFilter):
    title = ''
    parameter_name = ''

    def filter_lookups_queryset(self, request, qs):
        target_params = ('gender__exact', 'type__exact', 'age_range__exact', 'average_rating', 'vendor__id__exact',
                         'language__id__exact')
        initial_attrs = dict([(param, val) for param, val in request.GET.iteritems() if param in target_params and val])
        qs = qs.filter(**initial_attrs)
        status_attrs = dict([('selection__status', self.parameter_name.upper())])
        qs = qs.filter(**status_attrs).annotate(obj_count=Count('pk'))
        status_params = ('preapproved', 'approved', 'rejected')
        extra_status_attrs = [(param, val) for param, val in request.GET.iteritems()
                              if param in status_params and val and param != self.parameter_name]
        if len(extra_status_attrs) > 0:
            for item in extra_status_attrs:
                qs = qs.filter(id__in=Talent.objects
                               .filter(selection__status=item[0].upper())
                               .annotate(status_count=Count('selection__status'))
                               .filter(status_count=int(int(item[1]))))
        return qs

    def lookups(self, request, model_admin):
        qs = self.filter_lookups_queryset(request, model_admin.get_queryset(request))
        tuple_set = ()
        for number in sorted(qs.order_by().values_list('obj_count', flat=True).distinct()):
            tuple_set += ((number, str(number)),)
        return tuple_set

    def queryset(self, request, queryset):
        if self.value():
            qs = self.process_queryset(request, queryset)
            return qs
        else:
            return queryset

    def process_queryset(self, request, queryset):
        if hasattr(queryset[0], 'status_count'):
            qs = queryset.filter(id__in=Talent.objects
                                 .filter(selection__status=self.parameter_name.upper())
                                 .annotate(status_count=Count('selection__status'))
                                 .filter(status_count=int(request.GET[self.parameter_name])))
        else:
            qs = queryset.filter(selection__status=self.parameter_name.upper()).annotate(status_count=Count('pk'))
            qs = qs.filter(status_count=int(request.GET[self.parameter_name]))
        return qs


class PreapprovedFilter(StatusFilter):
    title = 'times preapproved'
    parameter_name = 'preapproved'


class ApprovedFilter(StatusFilter):
    title = 'times accepted'
    parameter_name = 'approved'


class RejectedFilter(StatusFilter):
    title = 'times rejected'
    parameter_name = 'rejected'


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
    list_filter = ('gender',
                   'type',
                   'age_range',
                   'average_rating',
                   InReviewFilter,
                   PreapprovedFilter,
                   ApprovedFilter,
                   RejectedFilter,
                   ('vendor', admin.RelatedOnlyFieldListFilter),
                   ('language', admin.RelatedOnlyFieldListFilter))
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


class CommentInline(admin.StackedInline):
    model = models.Comment
    readonly_fields = ('selection', 'author', 'text', 'created_date')
    extra = 0


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
