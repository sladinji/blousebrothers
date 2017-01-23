from django.db import models
from django.db.models import Count, Sum
from oscar.apps.catalogue.abstract_models import AbstractProduct
from django.utils.translation import ugettext_lazy as _
from cuser.middleware import CuserMiddleware

from blousebrothers.confs.models import Test


class Product(AbstractProduct):
    conf = models.ForeignKey('confs.Conference', related_name='products', default=None,
                             null=True)
    for_sale = models.BooleanField(default=False)
    interest_rating = models.SmallIntegerField(_("Intérêt global du dossier"), default=0)
    clarity_rating = models.SmallIntegerField(_("Clarté du dossier"), default=0)
    correction_rating = models.SmallIntegerField(_("Qualité de la correction"), default=0)
    difficulty_rating = models.SmallIntegerField(_("Difficulté du dossier"), default=0)

    def is_review_permitted(self, user):
        """
        Determines whether a user may add a review on this product.
        Default implementation respects OSCAR_ALLOW_ANON_REVIEWS and only
        allows leaving one review per user and product.
        Override this if you want to alter the default behaviour; e.g. enforce
        that a user purchased the product to be allowed to leave a review.
        """
        if user.is_authenticated() and self.conf and user.tests.filter(conf=self.conf) \
                and not self.conf.owner == user:
            return not self.has_review_by(user)
        else:
            return False

    def update_rating(self):
        """
        Recalculate rating field
        """
        self.rating = self.calculate_rating()
        self.interest_rating = self.calculate_rating('interest_score')
        self.clarity_rating = self.calculate_rating('clarity_score')
        self.correction_rating = self.calculate_rating('correction_score')
        self.difficulty_rating = self.calculate_rating('difficulty_score')
        self.save()
    update_rating.alters_data = True

    def calculate_rating(self, field='score'):
        """
        Calculate rating value
        """
        result = self.reviews.filter(
            status=self.reviews.model.APPROVED
        ).aggregate(
            sum=Sum(field), count=Count('id'))
        reviews_sum = result['sum'] or 0
        reviews_count = result['count'] or 0
        rating = None
        if reviews_count > 0:
            rating = float(reviews_sum) / reviews_count
        return rating

    def ratings(self):
        return (
            (_("Intérêt global du dossier"), self.interest_rating,),
            (_("Clarté du dossier"), self.clarity_rating,),
            (_("Qualité de la correction"), self.correction_rating,),
        )

    def get_title(self):
        if self.conf:
            return self.conf.title
        return super().get_title()

    def user_test(self):
        user = CuserMiddleware.get_user()
        if not user.is_anonymous():
            return Test.objects.get(student=user, conf=self.conf)

from oscar.apps.catalogue.models import *  # noqa
