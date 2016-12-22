from decimal import Decimal, ROUND_UP
from string import ascii_uppercase
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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
    return Decimal(test.score * 100 / test.max_score).quantize(Decimal('.01'), rounding=ROUND_UP)


@register.filter
def get_checked_fa(answer, test_answer):
    if str(answer.index) in test_answer.given_answers:
        return mark_safe('<i class="fa fa-check-square-o" aria-hidden="true"></i>')
    else:
        return mark_safe('<i class="fa fa-square-o" aria-hidden="true"></i>')


@register.filter
def sub_desc_custo(desc):
    return desc.replace('<p>', '<li>').replace('</p>', '</li>')
