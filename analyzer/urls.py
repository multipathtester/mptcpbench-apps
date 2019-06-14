from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^$', view=views.benchmark_info, name="benchmark"),
    url(regex=r'^mobility/$', view=views.mobility_info, name='mobility'),
    url(regex=r'^multipath/$', view=views.multipath_info, name="multipath"),
    url(regex=r'^mobility_detail/$', view=views.mobility_detail, name="mobility_detail"),
    url(regex=r'^mobility_detail_quic/$', view=views.quic_mobility_detail, name="quic_mobility_detail"),
]
