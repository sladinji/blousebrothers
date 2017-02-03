import logging

from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.contrib import messages

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


def check_bonus(request):
    try:
        bonus = request.user.handle_bonus()
        if bonus:
            messages.success(
                request,
                "Les {} € de bonus de ton abonnement t'ont été crédités.".format(bonus)
            )
    except Exception as ex:
        logger.error(ex, exc_info=True, extra={
            # Optionally pass a request and we'll grab any information we can
            'request': request,
        })
