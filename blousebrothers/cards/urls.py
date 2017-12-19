from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    url(regex=r'^$',
        view=RedirectView.as_view(url=reverse_lazy('cards:home'), permanent=True),
        name='root'
        ),
    url(regex=r'^partenariatnico$',
        view=views.BouletListView.as_view(),
        name='boulet'
        ),
    url(
        r'^mes/fiches$',
        view=views.ListCardView.as_view(),
        name='list'
    ),
    url(
        r'^fiches/oubliees$',
        view=views.ListTrashedCardView.as_view(),
        name='trashed'
    ),
    url(
        r'^fiches/nonvues$',
        view=views.UnseenCardsListView.as_view(),
        name='unseen_cards_list'
    ),
    url(
        regex=r'^fiches/(?P<pk>\d+)/fin/$',
        view=views.FinalizeCardView.as_view(),
        name='finalize'
    ),
    url(
        regex=r'^fiche/create/$',
        view=views.CreateCardView.as_view(),
        name='create'
    ),
    url(
        regex=r'^fiche/(?P<pk>\d+)/edit$',
        view=views.UpdateCardView.as_view(),
        name='update'
    ),
    url(
        regex=r'^fiche/(?P<id>\w+)/stop$',
        view=views.RevisionCloseSessionView.as_view(),
        name='stop'
    ),
    url(
        regex=r'^oublie/(?P<pk>\d+)$',
        view=views.RevisionDeleteView.as_view(),
        name='delete'
    ),
    url(
        regex=r'^fiches$',
        view=views.RevisionRedirectView.as_view(),
        name='redirect'
    ),
    url(
        regex=r'^letsgo$',
        view=views.RevisionRedirectView.as_view(),
        name='start_new_session'
    ),
    url(
        regex=r'^fiche/suivante/([0-9]+)$',
        view=views.RevisionNextCardView.as_view(),
        name='next'
    ),
    url(
        regex=r'^fiche/precedente/([0-9]+)$',
        view=views.RevisionPreviousCardView.as_view(),
        name='previous'
    ),
    url(
        regex=r'^fiche/(?P<id>\d+)/(?P<dsp_card_on_load>\w*)?$',
        view=views.RevisionView.as_view(),
        name='revision'
    ),
    url(
        regex=r'^fiche/bookmark/([0-9]+)$',
        view=views.bookmark_card,
        name='bookmark'
    ),
    url(
        regex=r'^anki$',
        view=views.AnkiUploadView.as_view(),
        name='ankiupload'
    ),

    url(
        regex=r'^dashboard$',
        view=views.RevisionHome.as_view(),
        name='home'
    ),
]
