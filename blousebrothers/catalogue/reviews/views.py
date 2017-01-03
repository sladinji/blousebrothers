from django.core.urlresolvers import reverse
from oscar.apps.catalogue.reviews.views import CreateProductReview as CoreCreateProductReview


class CreateProductReview(CoreCreateProductReview):

    def get_success_url(self):
        return reverse("confs:result", kwargs={'slug': self.product.conf.slug})
