from django.shortcuts import redirect
from django.core.urlresolvers import reverse
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
        if not self.request.user.is_authenticated \
                or self.request.user.is_authenticated and not self.request.user.has_full_access \
                and 'sort_by' not in self.request.GET:
            self.request.GET = self.request.GET.copy()
            self.request.GET.update(sort_by="price-asc")
        elif self.request.user.is_authenticated and self.request.user.has_full_access \
                and 'sort_by' not in self.request.GET:
            self.request.GET = self.request.GET.copy()
            self.request.GET.update(sort_by="newest")
        return super().get(*args, **kwargs)
