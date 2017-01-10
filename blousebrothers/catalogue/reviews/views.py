from django.core.urlresolvers import reverse
from oscar.apps.catalogue.reviews.views import CreateProductReview as CoreCreateProductReview


class CreateProductReview(CoreCreateProductReview):

    def get_success_url(self):
        return reverse("catalogue:detail", kwargs={'product_slug': self.product.slug,
                                                   'pk': self.product.id})
