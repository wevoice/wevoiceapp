import os
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout
from django.conf import settings
from django.conf.urls.static import static, serve
admin.autodiscover()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^admin/logout/', include('choices.urls')),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^', include('choices.urls'))
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = [
        url(r'^admin/logout/', include('choices.urls')),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('choices.urls'))
    ]

# for serving static files in development with DEBUG = False
if os.environ.get('LOCAL_MACHINE') and not settings.DEBUG:
    urlpatterns += [url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
                    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}), ]
