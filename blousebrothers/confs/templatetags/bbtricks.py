from decimal import Decimal, ROUND_UP
from string import ascii_uppercase

from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from oscar.core.loading import get_model

register = template.Library()
Product = get_model('catalogue', 'Product')


@register.filter
def to_char(value):
    return ascii_uppercase[value]


@register.filter
def is_good_css(answer, test_answer):
    if answer.correct and str(answer.index) in test_answer.given_answers or\
    not answer.correct and str(answer.index) not in test_answer.given_answers :
        return "correct"
    else:
        return "fatal" if answer.ziw else "notcorrect"


@register.filter
def zero_cause_error_label(answer, test_answer):
    if is_good_css(answer, test_answer) == "fatal":
        return mark_safe('( <i class="fa fa-warning" aria-hidden="true"></i> zéro sur cette mauvaise réponse) ')
    else:
        return ""


@register.filter
def result_icon(answer, test_answer):
    result = is_good_css(answer, test_answer)
    icon = '<big><i class="fa fa-{} pull-right big" aria-hidden="true"></i></big>'
    return {
        "correct": mark_safe(icon.format('check-circle')),
        "notcorrect": mark_safe(icon.format('warning')),
        "fatal": mark_safe(icon.format('heartbeat')),
    }[result]


@register.filter
def score100(test):
    if test.has_review():
        score = Decimal(test.score * 100 / test.max_score)
        span = '<span class="score"><big>{}</big> / 100</span>'.format(
            score.quantize(Decimal('.01'), rounding=ROUND_UP)
        )
        return mark_safe(span)
    else:
        return mark_safe(
            '<span class="score" href="{}#addreview">'
            'Laisse un avis pour accéder à ta note !</span>'
          )


@register.filter
def get_test_url(test):
    if not test.finished or test.has_review():
        return reverse('confs:test', kwargs={'slug': test.conf.slug})
    else:
        product = Product.objects.get(conf=test.conf)
        return reverse('catalogue:reviews-add', kwargs={
            'product_slug': product.slug, 'product_pk': product.id}
        ) + '#addreview'


@register.filter
def get_checked_fa(answer, test_answer):
    if str(answer.index) in test_answer.given_answers:
        return mark_safe('<i class="fa fa-check-square-o" aria-hidden="true"></i>')
    else:
        return mark_safe('<i class="fa fa-square-o" aria-hidden="true"></i>')


@register.filter
def sub_desc_custo(desc):
    """
    Make product's description display nice in subscription capsule
    """
    return desc.replace('<p>', '<li>').replace('</p>', '</li>')

@register.filter
def already_done(user, conf):
    try :
        return user.already_done(conf)
    except :
        return False
