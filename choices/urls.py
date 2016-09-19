from django.conf.urls import url

import views

urlpatterns = [
    # url(r'^updatedb/', views.updatedb, name='updatedb'),
    url(r'^$', views.user_login, name='user_login'),
    url(r'^delete_comment/$', views.delete_comment, name='delete_comment'),
    url(r'^(?P<client_name>[\w-]+)/$', views.index, name='index'),
    url(r'^(?P<client_name>[\w-]+)/for_approval/(?P<pk>[0-9]+)/$', views.for_approval, name='for_approval'),
    url(r'^(?P<client_name>[\w-]+)/for_approval/$', views.for_approval, name='for_approval'),
    url(r'^(?P<client_name>[\w-]+)/accepted/(?P<pk>[0-9]+)/$', views.accepted, name='accepted'),
    url(r'^(?P<client_name>[\w-]+)/accepted/$', views.accepted, name='accepted'),
    url(r'^(?P<client_name>[\w-]+)/rejected/$', views.rejected, name='rejected'),
    url(r'^(?P<client_name>[\w-]+)/add_comment/(?P<pk>[0-9]+)/$', views.add_comment, name='add_comment'),
    url(r'^(?P<client_name>[\w-]+)/delete_comment/(?P<pk>[0-9]+)/$', views.delete_comment, name='delete_comment')
]