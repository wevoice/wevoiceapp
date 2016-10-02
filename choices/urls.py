from django.conf.urls import url

import views

urlpatterns = [
    # url(r'^updatedb/$', views.updatedb, name='updatedb'),
    url(r'^$', views.user_login, name='user_login'),
    url(r'^add_comment/$', views.add_comment, name='add_comment'),
    url(r'^delete_comment/$', views.delete_comment, name='delete_comment'),
    url(r'^(?P<client_name>[\w-]+)/$', views.index, name='index'),
    url(r'^(?P<client_name>[\w-]+)/(?P<status>[\w-]+)(?:/(?P<pk>[0-9]+|))?/$', views.selections, name='selections')
]