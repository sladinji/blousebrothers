import hashlib
from datetime import datetime, timedelta
from mailchimp3 import MailChimp
from blousebrothers.users.models import User
from django.core.urlresolvers import reverse

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
    "telephone": "MMERGE4",
    "CODE5EUR": "MMERGE5",
    "is_conferencier": "MMERGE7",
    "MEMBER_RATING": "MMERGE8",
    "LATITUDE": "MMERGE9",
    "NOTES": "MMERGE10",
    "nombre ventes total": "MMERGE11",
    "nombre achats total": "MMERGE12",
    "gain de ce mois": "MMERGE13",
    "nombre ventes ce mois": "MMERGE14",
    "nombre achats ce mois": "MMERGE15",
    "ville": "MMERGE16",
    "moyenne notes conf": "MMERGE17",
    "nom conf entamee recente": "MMERGE18",
    "nombre jours depuis dernier achat": "MMERGE6",
    "MANGO_PAY": "MMERGE19",
    "needs_comment": "MMERGE20",
}


def clear(name):
    for m in client.lists.members.all(mc_lids[name], fields="members.id", get_all=True)['members']:
        print(m)
        client.lists.members.delete(mc_lids[name], m['id'])


def sync(qs=None, name='BlouseBrothers'):
    if not qs:
        qs = User.objects.all()
    for user in qs:
        needs_comment = "no"
        last_test = user.tests.last()
        try:
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
            tags['ville']: user.university.name if user.university else '',
            tags['pseudo']: user.username,
            tags['is_conferencier']: 'yes' if user.is_conferencier else 'no',
            tags["nombre ventes total"]: user.sales.count(),
            tags["nombre achats total"]: user.purchases.count(),
            tags["MANGO_PAY"]: 'OK' if user.gave_all_mangopay_info else 'NOK',
            tags["needs_comment"]: needs_comment,
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
