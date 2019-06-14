from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(
        regex=r'^create/$',
        view=views.BenchmarkCreateView.as_view(),
        name='create_benchmark'
    ),
    url(
        regex=r'^benchmarks/(?P<device_uuid>[0-9A-Fa-f-]+)$',
        view=views.BenchmarkListView.as_view(),
        name='list_benchmark'
    ),
    url(
        regex=r'^tests/(?P<benchmark_uuid>[0-9A-Fa-f-]+)$',
        view=views.TestListView.as_view(),
        name='list_tests'
    ),
    url(
        regex=r'^max_wifi_distance/$',
        view=views.MaxWifiDistanceView.as_view(),
        name='max_wifi_distance'
    ),
]
