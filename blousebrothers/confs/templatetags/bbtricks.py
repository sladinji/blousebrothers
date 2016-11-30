from string import ascii_uppercase
from django import template

register = template.Library()

@register.filter
def to_char(value):
    return ascii_uppercase[value]

@register.filter
def is_good(answer, test_answer):
    if answer.correct and str(answer.index) in test_answer.given_answers or\
    not answer.correct and str(answer.index) not in test_answer.given_answers :
        return "correct"
    else:
        return "notcorrect"
