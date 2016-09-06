from django.contrib import admin
import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'username', 'password')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 25
admin.site.register(models.Client, ClientAdmin)


class AppleAdmin(admin.ModelAdmin):
    list_display = ('id', 'talent', 'client', 'gender', 'age_range', 'language', 'sample_url', 'accepted', 'comment')
    list_display_links = ('id', 'talent')
    search_fields = ('talent', 'language', 'accepted')
    list_per_page = 25
admin.site.register(models.Apple, AppleAdmin)


class MainAdmin(admin.ModelAdmin):
    list_display = ('id', 'talent', 'client', 'gender', 'age_range', 'language', 'sample_url', 'accepted', 'comment')
    list_display_links = ('id', 'talent')
    search_fields = ('talent', 'client', 'language')
    list_per_page = 25
admin.site.register(models.Main, MainAdmin)


class VendorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'username', 'password')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 25
admin.site.register(models.Vendor, VendorAdmin)


class TalentAdmin(admin.ModelAdmin):
    list_display = ('id', 'welo_id', 'vendor_id', 'vendor_name', 'gender', 'age_range', 'language', 'sample_url',
                    'pre_approved', 'comment', 'allclients', 'rate', 'apple')
    list_display_links = ('id', 'welo_id')
    search_fields = ('welo_id', 'vendor_id', 'vendor_name', 'language')
    list_per_page = 25
admin.site.register(models.Talent, TalentAdmin)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'language')
    list_display_links = ('id', 'language')
    search_fields = ('language',)
    list_per_page = 25
admin.site.register(models.Language, LanguageAdmin)


admin.site.site_title = 'WeVoice Admin'
admin.site.site_header = 'WeVoice Admin'
