from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.catalogue.views import CatalogueView as CoreCatalogueView

from blousebrothers.tools import check_bonus


class ProductDetailView(CoreProductDetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        if obj.conf:
            context['meta'] = obj.conf.as_meta(self.request)
        return context


class CatalogueView(CoreCatalogueView):

    def get(self, *args, **kwargs):
        check_bonus(self.request, self.request.user)
        return super().get(*args, **kwargs)
