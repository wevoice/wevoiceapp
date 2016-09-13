from django.conf.urls import url

import views

urlpatterns = [
    # url(r'^updatedb/', views.updatedb, name='updatedb'),
    url(r'^$', views.user_login, name='user_login'),
    url(r'^(?P<client_name>[\w-]+)/$', views.index, name='index'),
    url(r'^(?P<client_name>[\w-]+)/for_approval/$', views.for_approval, name='for_approval'),
    url(r'^(?P<client_name>[\w-]+)/accepted/$', views.accepted, name='accepted'),
    url(r'^(?P<client_name>[\w-]+)/rejected/$', views.rejected, name='rejected')
]