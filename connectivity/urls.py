from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'$^',
        view=views.ConnectivityResultListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^test/$',
        view=views.ConnectivityTestCreateView.as_view(),
        name="create_test"
    )
]
