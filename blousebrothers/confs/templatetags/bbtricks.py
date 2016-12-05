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
def get_checked_fa(answer, test_answer):
    if str(answer.index) in test_answer.given_answers :
        return mark_safe('<i class="fa fa-check-square-o" aria-hidden="true"></i>')
    else :
        return mark_safe('<i class="fa fa-square-o" aria-hidden="true"></i>')
