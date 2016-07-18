from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login, name='login'),
    url(r'^account/(?P<id>[0-9]+)/$', views.account, name='account'),
]
