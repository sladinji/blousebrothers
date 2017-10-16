from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        regex=r'^$',
        view=views.FriendsView.as_view(),
        name='home'
    ),
    url(
        regex=r'^accept$',
        view=views.AcceptFriendsView.as_view(),
        name='accept_friend'
    ),
    url(
        regex=r'^refuse$',
        view=views.RefuseFriendsView.as_view(),
        name='refuse_friend'
    ),
    url(
        regex=r'^remove_friend$',
        view=views.RemoveFriendsView.as_view(),
        name='remove_friend'
    ),
    url(
        regex=r'^share_cards$',
        view=views.update_sharecards,
        name='share_cards'
    ),
    url(
        regex=r'^share_results$',
        view=views.update_shareresults,
        name='share_results'
    ),
    url(
        regex=r'^share_confs$',
        view=views.update_shareconfs,
        name='share_confs'
    ),
]
