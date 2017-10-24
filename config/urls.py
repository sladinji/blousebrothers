# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views import defaults as default_views
from django.contrib.sitemaps.views import sitemap

from paypal.express.dashboard.app import application as paypal

import blousebrothers.users.views
import blousebrothers.dashboard.orders.views
from blousebrothers.app import application

from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^subscriptions/$', TemplateView.as_view(template_name='pages/subscription.html'), name='subscriptions'),
    url(r'^hijack/', include('hijack.urls')),
    url(r'^robots\.txt', include('robots.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^rules/$', TemplateView.as_view(template_name='pages/regledujeu.html'), name='regledujeu'),
    url(r'^invitations/', include('invitations.urls', namespace='invitations')),
    url(
        regex=r'^FAQ/',
        view=blousebrothers.users.views.FAQ.as_view(),
        name='faq'
    ),


    # Terms and Conditions
    url(r'^terms/', include('termsandconditions.urls')),

    # Paypal
    url(r'^checkout/paypal/', include('paypal.express.urls')),
    url(r'^dashboard/paypal/express/', include(paypal.urls)),


    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^mon/', include('blousebrothers.users.urls', namespace='users')),
    url(r'^ecni/', include('blousebrothers.confs.urls', namespace='confs')),
    url(r'^accounts/', include('allauth.urls')),

    # URL change redirection
    url(r'^catalogue/', RedirectView.as_view(url='/ecni/catalogue/')),
    url(r'^search/', RedirectView.as_view(url='/ecni/catalogue/')),

    # Your stuff: custom urls includes go here
    url(r'^$', view=blousebrothers.users.views.SignupView.as_view(), name='home'),
    url(r'^demologin$', view=blousebrothers.users.views.DemoLoginView.as_view(), name='demologin'),
    url(r'', include(application.urls)),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^revisions/', include('blousebrothers.cards.urls', namespace='cards')),
    url(r'^communaute/', include('blousebrothers.friends.urls', namespace='friends')),
    url(r'^facture/(?P<pk>\d+)/$', view=blousebrothers.dashboard.orders.views.PDFView.as_view(), name="invoice"),
    url(r'^facture_pdf/(?P<pk>\d+)/$', view=blousebrothers.dashboard.orders.views.PDFViewPrintView.as_view(),
        name="invoice_pdf"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
