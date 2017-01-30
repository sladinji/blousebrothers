from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from django.apps import apps

statics = ['home', '@@@FAQ/' , '@@@cgu/', '@@@mentionslegales/']

Product = apps.get_model('catalogue', 'Product')

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        print("ahah")
        return statics + list(
            Product.objects.all().values_list("slug", "pk")
        )

    def location(self, item):
        if item not in statics:
            return reverse('catalogue:detail', kwargs={'product_slug':item[0], 'pk': item[1]})
        else :
            if item.startswith("@@@"):
                return item.replace("@@@","/")
            else :
                return reverse(item)
