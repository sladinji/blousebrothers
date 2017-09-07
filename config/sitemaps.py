from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from django.apps import apps

from blousebrothers.cards.models import Card

statics = ['home', '/FAQ/', '/cgu/', '/mentionslegales/']

Product = apps.get_model('catalogue', 'Product')


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return statics + list(
            Product.objects.all()
        ) + list(
            Card.objects.filter(public=True).all()
        )

    def location(self, item):
        if item not in statics:
            return item.get_absolute_url()
        else:
            if item.startswith("/"):
                return item
            else:
                return reverse(item)
