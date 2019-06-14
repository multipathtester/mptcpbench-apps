from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'$^', views.index, name='index'),
    url(r'^launch_test/', views.launch_test),
    url(r'^stop_nginx_server/', views.stop_nginx_server),
]
