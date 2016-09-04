from django.conf.urls import url

import views

urlpatterns = [
    # ex: /choices/
    url(r'^$', views.index, name='index'),
    # ex: /choices/5/
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail')
]