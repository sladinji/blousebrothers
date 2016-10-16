from string import ascii_uppercase
from django import template

register = template.Library()

@register.filter
def to_char(value):
    return ascii_uppercase[value]
