from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    url(regex=r'^$',
        view=RedirectView.as_view(url=reverse_lazy('friends:group'), permanent=False),
        name='root'
        ),
    url(
        regex=r'^amis/liste$',
        view=views.FriendsListView.as_view(),
        name='friend_list'
    ),
    url(
        regex=r'^amis$',
        view=views.FriendsView.as_view(),
        name='home'
    ),
    url(
        regex=r'^groupes$',
        view=views.GroupView.as_view(),
        name='group'
    ),
    url(
        regex=r'^groupes/update/(?P<pk>\d+)$',
        view=views.GroupUpdateView.as_view(),
        name='group_detail'
    ),
    url(
        regex=r'^groupes/create$',
        view=views.GroupCreateView.as_view(),
        name='create_group'
    ),
    url(
        regex=r'^accept_member$',
        view=views.AcceptMemberView.as_view(),
        name='accept_member'
    ),
    url(
        regex=r'^refuse_member$',
        view=views.RefuseMemberView.as_view(),
        name='refuse_member'
    ),
    url(
        regex=r'^accept_group_invit$',
        view=views.AcceptGroupInvit.as_view(),
        name='accept_group_invit'
    ),
    url(
        regex=r'^refuse_group_invit$',
        view=views.RefuseGroupInvitView.as_view(),
        name='refuse_group_invit'
    ),
    url(
        regex=r'^remove_member$',
        view=views.RemoveMemberView.as_view(),
        name='remove_member'
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
