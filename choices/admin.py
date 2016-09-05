from django.contrib import admin
import models

admin.site.register(models.Client)
admin.site.register(models.Apple)
admin.site.register(models.Main)
admin.site.register(models.Vendor)
admin.site.register(models.Talent)
admin.site.register(models.Language)

admin.site.site_title = 'WeVoice Admin'
admin.site.site_header = 'WeVoice Admin'
