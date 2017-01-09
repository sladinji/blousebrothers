from django.utils.translation import ugettext_lazy as _
from oscar.apps.catalogue.reviews.forms import ProductReviewForm as CoreProductReviewForm
from oscar.core.loading import get_model

ProductReview = get_model('reviews', 'productreview')


class ProductReviewForm(CoreProductReviewForm):
    class Meta:
        model = ProductReview
        fields = ('title', 'interest_score', 'clarity_score', 'correction_score',
                  'body', 'name', 'email')
        labels = {
            'body': _('Commentaires libres'),
            'title': _('Titre'),
        }
        help_texts = {
            'body': _('Pas de spoiler ! Merci :-)'),
            'title': _("Soit juste dans ton évaluation, c'est important :-) !"),
        }

    def scores(self):
        fields = list(self)
        return fields[1:4]
