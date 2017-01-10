from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.apps.catalogue.reviews.abstract_models import AbstractProductReview
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ProductReview(AbstractProductReview):
    interest_score = models.SmallIntegerField(
        _("Intérêt global du dossier"), choices=AbstractProductReview.SCORE_CHOICES,
        default=0)
    clarity_score = models.SmallIntegerField(
        _("Clarté du dossier"), choices=AbstractProductReview.SCORE_CHOICES,
        default=0)
    correction_score = models.SmallIntegerField(
        _("Qualité de la correction"), choices=AbstractProductReview.SCORE_CHOICES,
        default=0)

    # are between 0 and 5
    DIFFICULTY_CHOICES = tuple([(x, x) for x in range(0, 11)])
    difficulty_score = models.SmallIntegerField(
        _("Difficulté du dossier"), choices=DIFFICULTY_CHOICES,
        default=0)

    def scores(self):
        return (
            (_("Intérêt global du dossier"), self.interest_score,),
            (_("Clarté du dossier"), self.clarity_score,),
            (_("Qualité de la correction"), self.correction_score,),
        )


@receiver(pre_save, sender=ProductReview)
def set_score(sender, instance, *args, **kwargs):
    pr = instance
    total = pr.interest_score + pr.clarity_score + pr.correction_score
    pr.score = round(total / 3, 0)


from oscar.apps.catalogue.reviews.models import *  # noqa
