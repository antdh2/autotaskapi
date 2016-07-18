from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login, name='login'),
    url(r'^edit_account/(?P<id>[0-9]+)/$', views.edit_account, name='edit_account'),
    url(r'^account/(?P<id>[0-9]+)/$', views.account, name='account'),
]
