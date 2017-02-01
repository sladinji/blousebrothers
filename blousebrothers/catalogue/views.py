from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView


class ProductDetailView(CoreProductDetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        if obj.conf :
            context['meta'] = obj.conf.as_meta(self.request)
        return context
