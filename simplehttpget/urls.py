from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^test/$',
        view=views.SimpleHttpGetTestCreateView.as_view(),
        name="create_test"
    )
]
