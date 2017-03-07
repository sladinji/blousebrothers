import hashlib
from datetime import datetime, timedelta
from mailchimp3 import MailChimp
from blousebrothers.users.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum

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
    "has_conf_publiee": "MMERGE4",
    "present_sur_le_site": "MMERGE5",
    "nombre jours depuis dernier achat": "MMERGE6",
    "is_conferencier": "MMERGE7",
    "wallet_perso": "MMERGE8",
    "7d_since_last_buy": "MMERGE9",
    "3w_since_last_buy": "MMERGE10",
    "nombre ventes total": "MMERGE11",
    "nombre achats total": "MMERGE12",
    "gain de ce mois": "MMERGE13",
    "nombre ventes ce mois": "MMERGE14",
    "nombre achats ce mois": "MMERGE15",
    "ville": "MMERGE16",
    "moyenne notes conf": "MMERGE17",
    "nom conf entamee recente": "MMERGE18",
    "MANGO_PAY": "MMERGE19",
    "needs_comment": "MMERGE20",
    "6w_since_last_buy": "MMERGE21",
    "wallet_bonus": "MERGE22",
}


def clear(name):
    for m in client.lists.members.all(mc_lids[name], fields="members.id", get_all=True)['members']:
        print(m)
        client.lists.members.delete(mc_lids[name], m['id'])


def no_buy_since(user, days=7):
    lp = user.purchases.last()
    if lp:
        return lp.create_timestamp.replace(tzinfo=None) > datetime.now() - timedelta(days=days)


def days_since_last_purchase(user):
    lp = user.purchases.last()
    if lp:
        diff = datetime.today() - lp.create_timestamp.replace(tzinfo=None)
        return diff.days


def sync(qs=None, name='BlouseBrothers'):
    if not qs:
        qs = User.objects.all()
    for user in qs:
        # ACHATS DES 30 DERNIERS JOURS
        purchase30 = user.purchases.filter(
            create_timestamp__gt=datetime.now() - timedelta(days=30)
        ).count()
        # VENTES DES 30 DERNIERS JOURS
        sales30 = user.sales.filter(
            create_timestamp__gt=datetime.now() - timedelta(days=30)
        ).count()
        #  GAINS DES 30 DERNIERS JOURS
        won30 = user.sales.filter(
            create_timestamp__gt=datetime.now() - timedelta(days=10)
        ).aggregate(won=Sum('credited_funds'))['won']
        # DERNIER TEST COMMENTÉ ?
        needs_comment = None
        last_test = user.tests.last()
        # WALLETS
        wallet_perso = 0
        wallet_bonus = 0
        try:
            if user.gave_all_mangopay_info:
                wallet_perso = user.wallet.balance().amount
                wallet_bonus = user.wallet_bonus.balance().amount
            if last_test and not last_test.has_review() and last_test.conf.owner != user:
                product = last_test.conf.products.first()
                needs_comment = reverse('catalogue:reviews-add', kwargs={
                        'product_slug': product.slug, 'product_pk': product.id}
                    )
        except Exception as ex:
            print(ex)

        merge_fields = {
            'FNAME': user.first_name,
            'LNAME': user.last_name,
            tags['ville']: user.university.name if user.university else None,
            tags['pseudo']: user.username,
            tags['is_conferencier']: 'yes' if user.is_conferencier else None,
            tags["nombre ventes total"]: user.sales.count() if user.sales.count() else None,
            tags["nombre achats total"]: user.purchases.count() if user.purchases.count() else None,
            tags["MANGO_PAY"]: 'OK' if user.gave_all_mangopay_info else 'NOK',
            tags["needs_comment"]: needs_comment,
            tags["nombre ventes ce mois"]: sales30 if sales30 else None,
            tags["nombre achats ce mois"]: purchase30 if purchase30 else None,
            tags["gain de ce mois"]: won30 if won30 else None,
            tags["has_conf_publiee"]: user.created_confs.filter(for_sale=True).exists(),
            tags["wallet_perso"]: wallet_perso,
            tags["wallet_bonus"]: wallet_bonus,
            tags["present_sur_le_site"]: "yes",
            tags["7d_since_last_buy"]: no_buy_since(user, 7),
            tags["3w_since_last_buy"]: no_buy_since(user, 21),
            tags["6w_since_last_buy"]: no_buy_since(user, 42),
            tags["nombre jours depuis dernier achat"]: days_since_last_purchase(user),
        }
        print(merge_fields)

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
            if hasattr(ex, 'response'):
                print(ex.response.content)
            else:
                print(ex)


def last_48h():
    clear('test')
    qs = User.objects.filter(date_joined__gt=datetime.now() - timedelta(days=2))
    sync('test', qs)
