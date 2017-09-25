from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        regex=r'^amis$',
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
]
