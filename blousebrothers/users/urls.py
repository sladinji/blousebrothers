#detail -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    # URL pattern for the UserRedirectView
    url(
        regex=r'^compte/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView
    url(
        regex=r'^compte/(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the UserUpdateView
    url(
        regex=r'^profile/update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
    # Wallet
    #url(r'^wallet/$', TemplateView.as_view(template_name='pages/wallet_teaser.html'), name='wallet'),
    url(
        regex=r'^wallet/$',
        view=views.UserWalletView.as_view(),
        name='wallet'
    ),
    # IBAN
    url(
        regex=r'^wallet/addbankaccount/$',
        view=views.AddIbanView.as_view(),
        name='addiban'
    ),
    # PAYOUT
    url(
        regex=r'^wallet/transfert/$',
        view=views.PayOutView.as_view(),
        name='payout'
    ),
    # Credit Card
    url(
        regex=r'^wallet/addcard/$',
        view=views.AddCardView.as_view(),
        name='addcard'
    ),
    # MangoPay Credit Card feed back
    url(
        regex=r'^wallet/addcardreturn/$',
        view=views.HandleMangoAddCardReturn.as_view(),
        name='addcardreturn'
    ),
    # Subscription
    url(
        regex=r'^abonnement/(?P<sub_id>[\d]*)$',
        view=views.Subscription.as_view(),
        name='subscription'
    ),
    # Inviations
    url(
        regex=r'^invitation/$',
        view=views.UserSendInvidation.as_view(),
        name='invitation'
    ),
    # SpecialOffer demand
    #url(
    #    regex=r'^specialoffer/$',
    #    view=views.SpecialOffer.as_view(),
    #    name='specialoffer'
    #),
    # ActivateOffer demand
    #url(
    #    regex=r'^activate/(?P<user_id>[\d]*)$',
    #    view=views.ActivateOffer.as_view(),
    #    name='activateoffer'
    #),
    # FAQ
    url(
        regex=r'^~FAQ$',
        view=views.FAQ.as_view(),
        name='faq'
    ),
    # WIEWS
    url(
       regex=r'^stats$',
       view=views.Stats.as_view(),
       name='stats',
    ),
  ]

