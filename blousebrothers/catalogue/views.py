from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView


class ProductDetailView(CoreProductDetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta'] = self.get_object().conf.as_meta(self.request)
        return context
