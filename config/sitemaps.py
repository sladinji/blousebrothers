from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from blousebrothers.confs.models import Conference

statics = ['home', 'about']


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return statics + list(Conference.objects.values_list("slug", flat=True))

    def location(self, item):
        if item not in statics:
            return reverse('confs:detail', kwargs={'slug':item})
        return reverse(item)
