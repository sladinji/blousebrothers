import logging

from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def analyse_conf(conf):
    total_q = len(conf.questions.all())
    written_q = [q for q in conf.questions.all() if q.question]
    valid_q = [q for q in written_q if q.is_valid()]
    """ valid question mean question with a valid answer """
    progress = len(valid_q) / total_q * 100
    conf.edition_progress = int(progress)
    conf.save()
    confdict = model_to_dict(conf)
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
    if not user.is_authenticated():
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
            ctx = dict(bonus=bonus)
            msg_plain = render_to_string('confs/email/bonus.txt', ctx)
            msg_html = render_to_string('confs/email/bonus.html', ctx)
            send_mail(
                    'Crédit BlouseBrothers',
                    msg_plain,
                    'noreply@blousebrothers.fr',
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
            send_mail(
                    'Bonus filleul',
                    msg_plain,
                    'noreply@blousebrothers.fr',
                    [invitation.inviter.email],
                    html_message=msg_html,
            )
    except Exception as ex:
        logger.error(ex, exc_info=True, extra={
            # Optionally pass a request and we'll grab any information we can
            'request': request,
        })
