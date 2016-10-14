import re
from django import template

register = template.Library()

@register.filter(name='youtube')
def youtube(value):
    if 'youtube' in value:
        value = re.sub(r'<img class="ta-insert-video" src="[^"]*" ta-insert-video="([^"]*)" allowfullscreen="true"[^>]*>',
                       r'<iframe width="420" height="315" src="\1" allowfullscreen="true"></iframe>',
                        value)
    return value

