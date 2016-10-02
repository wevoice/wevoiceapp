from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static, serve
import debug_toolbar
admin.autodiscover()

if settings.DEBUG:
    urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^', include('choices.urls'))
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('choices.urls'))
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Uncomment for serving static files in development with DEBUG = False
    # urlpatterns += [url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
    #                 url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}), ]
