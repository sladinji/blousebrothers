import re
import hashlib
from datetime import datetime, timedelta
from mailchimp3 import MailChimp
from blousebrothers.users.models import User
from django.db.models import Sum
from django.utils import timezone
from django.template.loader import get_template


import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

LIST_NAME = 'BlouseBrothers'

# MailChimp clien API

client = MailChimp('Guillaume', '1f44b79db423b0c889fb301564eb969a-us12')

#  Dictionnary { "mailing list name": "mailing list id"}

mc_lids = {
    x['name']: x['id']
    for x in client.lists.all(
        get_all=True,
        fields="lists.name,lists.id"
    )['lists']
}

tags = {
    "pseudo": "MMERGE3",
    "gain de ce mois": "MMERGE13",
    "ville": "MMERGE16",
    "moyenne notes conf": "MMERGE17",
    "status": "MMERGE25",
    "action": "MMERGE28",
    "conf_entam_url": "MMERGE29",
    "conf_pub_url": "MMERGE30",
    "conf_encours_url": "MMERGE4",
    "last_dossier_url": "MMERGE24",
    "nombre_fiches": "MMERGE5",
    "status_fiches": "MMERGE6",
    "preview_fiches": "MMERGE7",
}


def clear(name):
    for m in client.lists.members.all(mc_lids[name], fields="members.id", get_all=True)['members']:
        print(m)
        client.lists.members.delete(mc_lids[name], m['id'])


def update_status(status, new_suffix):
    return "{}{}".format(re.sub('_H24|_J7|_J15|_M1|_inact', '', status), new_suffix)


def special_status(user):
    """Special status don't follow usual incrementation"""
    now = timezone.now()
    for current_status, next_status in (
        ('conf_publi_ok', 'creat_wait'),
        ('conf_sold', 'creat_wait'),
        ('get_eval_ok', 'creat_wait'),
        ('buyer_ok_M1', 'money_ok'),
    ):
        if user.status == current_status and now - user.status_timestamp > timedelta(hours=24):
            user.status = next_status
            return True
    logger.info("No special status")


def increment_status(user):
    """Update _inact suffix according to  user status timestamp"""
    now = timezone.now()
    logger.info('user status age : %s', now - user.status_timestamp)
    if now - user.status_timestamp > timedelta(days=15) and user.status.endswith("_M1"):
        logger.info('inact')
        user.status = "inact"
    elif now - user.status_timestamp > timedelta(days=14) and user.status.endswith("_J15"):
        logger.info('_M1')
        user.status = update_status(user.status, "_M1")
    elif now - user.status_timestamp > timedelta(days=8) and user.status.endswith("_J7"):
        logger.info('_J15')
        user.status = update_status(user.status, "_J15")
    elif now - user.status_timestamp > timedelta(days=6) and user.status.endswith("_H24"):
        logger.info('_J7')
        user.status = update_status(user.status, "_J7")
    elif now - user.status_timestamp > timedelta(hours=24) and not user.status.endswith("_H24"):
        logger.info('_H24')
        user.status = update_status(user.status, "_H24")


def handle_status(user):
    now = timezone.now()
    if not user.status_timestamp:
        user.status_timestamp = now
    if not special_status(user):
        increment_status(user)
    user.mailchync = False  # disable mailchync on save
    user.save()  # status_timestamp updated when status change


def sync(qs=None, name=LIST_NAME):
    if not qs:
        qs = User.objects.all()
    now = datetime.now()
    for user in qs:
        if "yopmail.com" in user.email:
            continue
        #  GAINS DES 30 DERNIERS JOURS
        won30 = user.sales.filter(
            create_timestamp__gt=now - timedelta(days=10)
        ).aggregate(won=Sum('credited_funds'))['won']
        handle_status(user)

        #  CARDS REVISION PREVIEW
        card_ready_qry = user.deck.filter(wake_up__gt=now-timedelta(days=1), wake_up__lt=now)
        nb_new_cards_ready = card_ready_qry.count()
        html_preview_cards = get_template('cards/emails/preview_cards.html')
        context = {'previews': [x.card.content.split('\n')[0].replace("@", "")
                                for x in card_ready_qry[:10]
                                ]
                   }

        merge_fields = {
            'FNAME': user.first_name,
            'LNAME': user.last_name,
            tags['ville']: user.university.name if user.university else None,
            tags['pseudo']: user.username,
            tags["gain de ce mois"]: won30 if won30 else None,
            tags["status"]: user.status,
            tags["action"]: user.action,
            tags["conf_entam_url"]: user.conf_entam_url,
            tags["conf_pub_url"]: user.conf_pub_url,
            tags["conf_encours_url"]: user.conf_encours_url,
            tags["last_dossier_url"]: user.last_dossier_url,
            tags["nombre_fiches"]: nb_new_cards_ready,
            tags["status_fiches"]: "go" if nb_new_cards_ready > 0 else "nogo",
            tags["preview_fiches"]: html_preview_cards.render(context),
        }
        merge_fields = {k: v for k, v in merge_fields.items() if v}
        logger.info(merge_fields)

        try:
            client.lists.members.create_or_update(
                mc_lids[name],
                subscriber_hash=hashlib.md5(user.email.lower().encode()).hexdigest(),
                data={
                    'email_address': user.email,
                    'status_if_new': 'subscribed',
                    'merge_fields': merge_fields,
                })
        except Exception as ex:
            if hasattr(ex, 'response') and ex.response:
                logger.exception(ex.response.content)
            else:
                logger.exception(ex)


def last_48h():
    clear('test')
    qs = User.objects.filter(date_joined__gt=datetime.now() - timedelta(days=2))
    sync('test', qs)


def reset_workflow():
    """
    Reset mailchimp status according to current state.
    """
    User.objects.filter(mangopay_users__isnull=True).update(status="registered")
    for user in User.objects.filter(mangopay_users__isnull=False):
        if not user.gave_all_mangopay_info():
            user.status = 'registered'
            user.save()
            continue
        if user.created_confs.filter(edition_progress=100, for_sale=False).exists():
            user.status = 'creat_conf_100'
            user.save()
            continue
        if user.created_confs.filter(edition_progress__lt=100).exists():
            user.status = 'creat_conf_begin'
            user.save()
            continue
        if user.created_confs.filter(edition_progress=100, for_sale=True).exists():
            user.status = 'conf_publi_ok'
            user.save()
            continue
        if user.balance().amount == 0:
            user.status = 'wallet_ok'
            user.save()
            continue
        elif [rev for rev in user.tests.all() if not rev.has_review()]:
            user.status = 'give_eval_notok'
            user.save()
            continue
        else:
            user.status = 'money_ok'
            user.save()
            continue
