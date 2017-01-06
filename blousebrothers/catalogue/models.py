from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    conf = models.ForeignKey('confs.Conference', related_name='products', default=None,
                             null=True)
    for_sale = models.BooleanField(default=False)

    def is_review_permitted(self, user):
        """
        Determines whether a user may add a review on this product.
        Default implementation respects OSCAR_ALLOW_ANON_REVIEWS and only
        allows leaving one review per user and product.
        Override this if you want to alter the default behaviour; e.g. enforce
        that a user purchased the product to be allowed to leave a review.
        """
        if user.is_authenticated() and self.conf and user.tests.filter(conf=self.conf):
            return not self.has_review_by(user)
        else:
            return False

    def get_title(self):
        if self.conf:
            return self.conf.title
        return super().get_title()

from oscar.apps.catalogue.models import *  # noqa
