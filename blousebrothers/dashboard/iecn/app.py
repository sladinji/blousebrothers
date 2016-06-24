from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class


class IECNApplication(Application):
    name = None

    default_permissions = ['partner.dashboard_access', ]
    iecn_createupdate_view = get_class('dashboard.iecn.views',
                                          'IECNCreateUpdateView')

    def get_urls(self):
        urls = [
            url(r'^iecn/(?P<pk>\d+)/$',
                self.iecn_createupdate_view.as_view(),
                name='catalogue-product'),
        ]
        return self.post_process_urls(urls)


application = IECNApplication()
