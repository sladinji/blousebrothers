from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^liste/?$',
        view=views.ListCardView.as_view(),
        name='list'
    ),
    url(
        regex=r'^create/$',
        view=views.CreateCardView.as_view(),
        name='create'
    ),
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/edit$',
        view=views.UpdateCardView.as_view(),
        name='update'
    ),
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/fiche$',
        view=views.DetailCardView.as_view(),
        name='detail'
    ),
]
