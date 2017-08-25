from django.conf.urls import url
from oscar import app


class BBShop(app.Shop):
    # Override get_urls method
    def get_urls(self):
        """
        Replace catalogue URL (first one in original func)
        """
        urls = [url(r'^ecni/catalogue/', self.catalogue_app.urls)] + super().get_urls()[1:]
        return urls

application = BBShop()
