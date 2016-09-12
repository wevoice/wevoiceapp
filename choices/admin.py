from django.contrib import admin
import models


class TalentAdmin(admin.ModelAdmin):
    list_display = ('id', 'welo_id', 'vendor_fk', 'pre_approved', 'language')
    exclude = ('vendor_id', 'gender', 'age_range', 'language', 'sample_url', 'comment', 'allclients', 'rate')
    list_display_links = ('id', 'welo_id')
    search_fields = ('welo_id', 'vendor_id', 'vendor_name', 'language', 'client__name', 'client__username')
    list_per_page = 25
admin.site.register(models.Talent, TalentAdmin)


class ClientAdmin(admin.ModelAdmin):
    exclude = ('talents', 'password')
    list_display = ('id', 'name', 'username')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'username')
    list_per_page = 25
admin.site.register(models.Client, ClientAdmin)


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


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'language')
    list_display_links = ('id', 'language')
    search_fields = ('language',)
    list_per_page = 25
admin.site.register(models.Language, LanguageAdmin)


class SelectionAdmin(admin.ModelAdmin):
    list_display = ('talent', 'client', 'status')
admin.site.register(models.Selection, SelectionAdmin)

admin.site.site_title = 'WeVoice Admin'
admin.site.site_header = 'WeVoice Admin'
