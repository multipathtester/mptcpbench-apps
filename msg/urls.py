from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^test/$',
        view=views.MsgTestCreateView.as_view(),
        name="create_test"
    )
]
