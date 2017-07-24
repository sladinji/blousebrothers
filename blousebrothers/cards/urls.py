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
        regex=r'^$',
        view=views.RevisionRedirectView.as_view(),
        name='redirect'
    ),
    url(
        regex=r'^(?P<slug>[\w.@+-]+)/fiche$',
        view=views.RevisionView.as_view(),
        name='revision'
    ),
    url(
        regex=r'^bookmark/([0-9]+)$',
        view=views.bookmark_card,
        name='bookmark'
    ),
]
