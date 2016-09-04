from django.contrib import admin
import models

admin.site.register(models.Question)

admin.site.site_title = 'WeVoice Admin'
admin.site.site_header = 'WeVoice Admin'
