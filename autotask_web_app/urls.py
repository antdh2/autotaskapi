from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^autotask_login/$', views.autotask_login, name='autotask_login'),
    url(r'^$', views.index, name='index'),
    url(r'^create_ticket/(?P<id>[0-9]+)/$', views.create_ticket, name='create_ticket'),
    url(r'^create_home_user_ticket/(?P<id>[0-9]+)/', views.create_home_user_ticket, name='create_home_user_ticket'),
    url(r'^edit_account/(?P<id>[0-9]+)/$', views.edit_account, name='edit_account'),
    url(r'^account/(?P<id>[0-9]+)/$', views.account, name='account'),
]
