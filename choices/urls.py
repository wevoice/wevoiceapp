from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<client_name>[\w-]+)/$', views.detail, name='detail'),
    url(r'^(?P<client_name>[\w-]+)/for_approval/$', views.for_approval, name='for_approval'),
    url(r'^(?P<client_name>[\w-]+)/accepted/$', views.accepted, name='accepted'),
    url(r'^(?P<client_name>[\w-]+)/rejected/$', views.rejected, name='rejected')
]