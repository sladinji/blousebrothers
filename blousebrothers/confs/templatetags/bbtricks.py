from decimal import Decimal, ROUND_UP
import re
from string import ascii_uppercase
import datetime

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum
from django.contrib.staticfiles.templatetags.staticfiles import static
from oscar.core.loading import get_model

from blousebrothers.tools import get_disqus_sso as get_remote_auth

register = template.Library()
Product = get_model('catalogue', 'Product')


@register.filter
def to_char(value):
    return ascii_uppercase[value]


@register.filter
def or_subscription(money):
    """
    Display Abo in conferencier sale's table when amount == 0.
    """
    if money.amount == 0:
        return "Abo*"
    else:
        return money.amount


@register.filter
def default_icon(name):
    if not name:
        return static('images/ms-icon-150x150.png')
    else:
        return name


@register.filter
def is_good_css(answer, test_answer):
    if answer.correct and str(answer.index) in test_answer.given_answers \
            or not answer.correct and str(answer.index) not in test_answer.given_answers:
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
    if test.finished:
        score = Decimal(test.score * 100 / test.max_score).quantize(Decimal('.01'), rounding=ROUND_UP)
        span = '<span class="score"><big>{}</big> / 100</span>'.format(score)
        return mark_safe(span)
    else:
        return ""


@register.filter
def get_test_url(test):
    try:
        if not test.finished or test.has_review():
            return reverse('confs:test', kwargs={'slug': test.conf.slug})
        else:
            product = Product.objects.get(conf=test.conf)
            return reverse('catalogue:reviews-add', kwargs={
                'product_slug': product.slug, 'product_pk': product.id}
            ) + '#addreview'
    except:
        return ""


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
    try:
        return user.already_done(conf)
    except:
        return False


@register.filter
def test_finished(user, conf):
    try:
        test = user.tests.get(conf=conf)
        return test.finished
    except:
        return False


@register.filter
def today_sales(conf):
    today = datetime.date.today()
    qs = conf.owner.sales.filter(product__conf=conf)
    qs = qs.filter(create_timestamp__day=today.day,
                   create_timestamp__month=today.month,
                   create_timestamp__year=today.year)
    return qs.count()


@register.filter
def week_sales(conf):
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    qs = conf.owner.sales.filter(product__conf=conf)
    qs = qs.filter(create_timestamp__gte=last_week)
    return qs.count()


@register.filter
def month_revenu(conf):
    today = datetime.date.today()
    qs = conf.owner.sales.filter(product__conf=conf)
    qs = qs.filter(create_timestamp__month=today.month,
                   create_timestamp__year=today.year)
    return qs.aggregate(Sum('credited_funds'))['credited_funds__sum']


@register.filter
def wallet_clean(wallet_balance):
    return str(wallet_balance).replace("EUR ", "")


@register.filter
def sort_items(d):
    try:
        return sorted(d, key=lambda x: int(x['name']))
    except:
        return sorted(d, key=lambda x: x['name'])


@register.simple_tag
def get_remote_s3(user):
    return get_remote_auth(user)


@register.simple_tag
def get_disqus_sso(user):
    # return a script tag to insert the sso message
    return mark_safe("""<script type="text/javascript">
                     var disqus_config = function() {
                     this.page.remote_auth_s3 = "%(remote_auth)s";
                     this.page.api_key = "%(pub_key)s";
                     }
                     </script>""" % dict(
                         remote_auth=get_remote_auth(user),
                         pub_key=settings.DISQUS_PUBLIC_KEY,
                     )
                     )


# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.filter
def rev_content(txt):
    #  Preview first line if no @ are present in text
    if "@" not in txt:
        txt = re.sub(r"(.+)\n", r"@@\1@@", txt, 1)
    #  Replace - by font awesome >
    txt = re.sub("(?m)^-(.*)", r'<i class="fa fa-chevron-right" aria-hidden="true"></i> \1<br>', txt)
    #  Add when txt is indented by space or tab
    for i in range(1, 5):
        txt = re.sub(r'(?m)^\t{%s}([^\t]+)' % i,
                     '&nbsp;'*4*i + r'<i class="fa fa-check" aria-hidden="true"></i> \1', txt)
        txt = re.sub(r'(?m)^ {%s}([^ ]+)' % i,
                     '&nbsp;'*i + r'<i class="fa fa-check" aria-hidden="true"></i> \1', txt)
    #  Replace @@ by preview span
    txt = re.sub("([^@]*)@@([^@]*)@@", r"\1</span><span class='preview'>\2</span><span><br>", txt)
    #  Replace new lines by <br>
    txt = re.sub("\n", r"<br>", txt)
    # Replace /!\ by icon
    txt = re.sub(r'/!\\', '<i class="fa fa-exclamation-triangle" aria-hidden="true"></i> ', txt)
    return txt
