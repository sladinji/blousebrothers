import logging
import simplejson
import base64
import hashlib
import hmac
import time

from django.forms.models import model_to_dict
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def bbmail(title, msg_plain, dests, html_message=None, tags=None):
    email = EmailMultiAlternatives(
            title,
            msg_plain,
            '<BlouseBrothers contact@blousebrothers.fr>',
            dests,
    )
    if html_message:
        email.attach_alternative(html_message, "text/html")
    if tags:
        email.extra_headers['X-Mailgun-Tag'] = tags
    email.send()


def analyse_conf(conf):
    total_q = len(conf.questions.all())
    written_q = [q for q in conf.questions.all() if q.question]
    valid_q = [q for q in written_q if q.is_valid()]
    """ valid question mean question with a valid answer """
    progress = len(valid_q) / total_q * 100
    conf.edition_progress = int(progress)
    conf.save()
    confdict = model_to_dict(conf)
    confdict.pop('specialities')
    confdict.pop('items')
    confdict.update(pk=conf.id)  # to be compatible with djng rest api
    return {
        'total_q': total_q,
        'written_q': [q.id for q in written_q],
        'valid_q': [q.id for q in valid_q],
        'conference': confdict,
    }


def get_full_url(request, view_name, **kwargs):
    return '{}{}{}'.format(
        'https://' if request.is_secure() else 'http://',
        request.get_host(),
        reverse(view_name, **kwargs)
    )


def check_bonus(request=None, user=None, sub=None):
    if request and not user:
        user = request.user
    if not user.is_authenticated:
        return
    if not sub:
        sub = user.subscription
    try:
        bonus = user.handle_subscription_bonus(sub)
        if bonus:
            if request:
                messages.success(
                    request,
                    "Les {} € de bonus de ton abonnement t'ont été crédités.".format(bonus)
                )
            ctx = dict(bonus=bonus, user=user)
            msg_plain = render_to_string('confs/email/bonus.txt', ctx)
            msg_html = render_to_string('confs/email/bonus.html', ctx)
            bbmail(
                    'Bonus BlouseBrothers',
                    msg_plain,
                    [user.email],
                    html_message=msg_html,
            )
    except Exception as ex:
        logger.error(ex, exc_info=True, extra={
            # Optionally pass a request and we'll grab any information we can
            'request': request,
        })
    try:
        invitation = user.handle_sponsor_bonus(sub)
        if invitation:
            ctx = dict(sponsored=user,
                       sponsor=invitation.inviter,
                       bonus=sub.type.bonus_sponsor,
                       sub=sub,
                       )
            msg_plain = render_to_string('confs/email/bonus_sponsor.txt', ctx)
            msg_html = render_to_string('confs/email/bonus_sponsor.html', ctx)
            bbmail(
                    'Bonus filleul',
                    msg_plain,
                    [invitation.inviter.email],
                    html_message=msg_html,
            )
    except Exception as ex:
        logger.error(ex, exc_info=True, extra={
            # Optionally pass a request and we'll grab any information we can
            'request': request,
        })


def get_disqus_sso(user):
    """
    Return remote_auth value required by Disqus API for SSO user authentication.
    """
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }
    # create a JSON packet of our data attributes
    data = simplejson.dumps(user_data)
    # generate a timestamp for signing the message
    timestamp = int(time.time())
    message = base64.b64encode(data.encode("utf-8")).decode(),
    return "{message} {signature} {timestamp}".format(
        timestamp=timestamp,
        message=message,
        signature=hmac.HMAC(settings.DISQUS_SECRET_KEY.encode("utf-8"),
                            "{} {}".format(message, timestamp).encode("utf-8"),
                            hashlib.sha1).hexdigest()
    )
