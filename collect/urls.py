from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'$^', views.index, name='index'),
    # URLs related to user accounts
    url(r'^login/$', auth_views.login, name='login', kwargs={'template_name': 'collect/login.html', 'redirect_authenticated_user': True}),
    url(r'^logout/$', auth_views.logout, {'template_name': 'collect/logout.html'}, name='logout'),
    url(r'^sign_up/$', views.sign_up, name='sign_up'),
    # Smartphone URLs
    url(r'^smartphone_results_graphs/$', views.smartphone_results_graphs),
    url(r'^smartphone_results_graphs/get_graph/$', views.get_graph_smartphone),
    url(r'^smartphone_passive_results_details/(?P<config_id>[0-9]+)/(?P<server_ip>[0-9.-]+)/$', views.smartphone_passive_results_details),
    url(r'^smartphone_passive_results_details/(?P<config_id>[0-9]+)/(?P<server_ip>[0-9.-]+)/get_graph/$', views.get_graph_smartphone_passive),
    url(r'^msg_result/(?P<test_id>[0-9]+)/$', views.get_msg_result),
    # Other URLs
    url(r'^save_test/', views.save_test),
    url(r'^upload_client_trace/(?P<store_path>.*)/$', views.upload_client_trace),
    url(r'^upload_server_trace/(?P<store_path>.*)/$', views.upload_server_trace),
    url(r'^upload_undefined_trace/(?P<store_path>.*)/$', views.upload_undefined_trace),
    url(r'^upload_smartphone_trace/(?P<store_path>.*)/$', views.upload_smartphone_trace),
    url(r'^get_next_experiments/', views.get_next_experiments),
    url(r'^get_public_ip/', views.get_public_ip),
    url(r'^no_test_results/(?P<uploader_email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<test_id>[0-9]+)/$', views.no_test_results_details),
    url(r'^no_test_results/(?P<uploader_email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<test_id>[0-9]+)/get_graph/$', views.get_graph),
    url(r'^no_test_results/(?P<uploader_email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.no_test_results, name='no_test_results'),
    url(r'^no_test_upload/$', views.no_test_upload, name='no_test_upload'),
]
