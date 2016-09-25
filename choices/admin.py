from django.contrib import admin
import models

from django.forms import Textarea
from django.db import models as dbmodels


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'client', 'vendor', 'email', 'is_active', 'is_staff', 'is_superuser',
                    'date_joined', 'last_login')
    list_display_links = ('user',)
    list_filter = ('client',)
    search_fields = ('client__name', 'client__username', 'user__username', 'user__first_name')
    list_per_page = 100
admin.site.register(models.UserProfile, UserProfileAdmin)


class ClientAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':50})},
    }
    list_display = ('id', 'name', 'username', 'password')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 100
admin.site.register(models.Client, ClientAdmin)


class MainAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':50})},
    }
    list_display = ('id', 'talent', 'client', 'gender', 'age_range', 'language', 'sample_url', 'accepted', 'comment')
    list_display_links = ('id', 'talent')
    search_fields = ('talent', 'client', 'language')
    list_per_page = 100
admin.site.register(models.Main, MainAdmin)


class VendorAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':50})},
    }
    list_display = ('id', 'name', 'username', 'password')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 100
admin.site.register(models.Vendor, VendorAdmin)


class LanguageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':50})},
    }
    list_display = ('id', 'language')
    list_display_links = ('id', 'language')
    search_fields = ('language',)
    list_per_page = 100
admin.site.register(models.Language, LanguageAdmin)


class TalentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(TalentAdmin, self).get_queryset(request)
        if request.user.userprofile.vendor:  # If the user has a vendor
            # change the queryset for this modeladmin
            qs = qs.filter(vendor_name=request.user.userprofile.vendor.name)
        return qs

    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':50})},
    }
    list_filter = ('gender', 'type', 'age_range', 'vendor', 'language')
    list_display = ('id', 'welo_id', 'vendor', 'audio_file_player', 'language', 'type', 'gender', 'old_talent_id')
    list_display_links = ('id', 'welo_id')
    search_fields = ('welo_id', 'vendor__name', 'language', 'sample_url', 'old_talent_id')
    list_per_page = 100

    def get_actions(self, request):
        actions = super(TalentAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    class Media:
        js = ('js/admin/extra-admin.js',)
        css = {
             'all': ('css/admin/extra-admin.css',)
        }
admin.site.register(models.Talent, TalentAdmin)


class SelectionAdmin(admin.ModelAdmin):
    list_filter = ('status', 'talent__gender', 'client__name', 'talent__vendor', 'talent__language', )
    list_display = ('id', 'talent', 'client', 'status', 'audio_file_player', 'talent_language', 'talent_gender',
                    'talent_vendor', 'talent_age_range')
    search_fields = ['client__username', 'client__name', 'talent__welo_id', 'talent__vendor__name']

    class Media:
        js = ('js/admin/extra-admin.js',)
        css = {
             'all': ('css/admin/extra-admin.css',)
        }
admin.site.register(models.Selection, SelectionAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created_date')
    search_fields = ['post']
admin.site.register(models.Comment, CommentAdmin)


admin.site.site_title = 'WeVoice Admin'
admin.site.site_header = 'WeVoice Admin'



