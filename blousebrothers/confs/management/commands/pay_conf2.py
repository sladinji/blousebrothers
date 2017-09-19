from decimal import Decimal
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from blousebrothers.confs.models import Subscription


def get_monthly_amount(sub):
    """
    Return amount divided by number of available month
    """
    price = sub.price_paid / Decimal('1.2') * Decimal('0.7')
    nb_month = max([(sub.date_over - sub.date_created).days//30, 1])
    return (price / nb_month).quantize(Decimal('1.00'))


class Command(BaseCommand):
    """
    For each subscription we calculate how much a user has to give to a conferencier.
    """
    help = 'Pay conferenciers according to on going subscriptions'

    def handle(self, *args, **options):
        yesterday = datetime.now() - timedelta(days=1)
        two_days_ago = datetime.now() - timedelta(days=2)
        for sub in Subscription.objects.filter(
            date_over__day=yesterday.day,
            date_over__gt=two_days_ago,
        ).all():
            total_amount = get_monthly_amount(sub)
            nb_purchases = Decimal(sub.user.purchases.filter(credited_funds=0).count())
            if not nb_purchases:
                continue
            shared_amount = total_amount / nb_purchases
            for sale in sub.user.purchases.filter(credited_funds=0):
                transfer = sale.conf.owner.credit_wallet(shared_amount)
                sale.credited_funds = shared_amount
                sale.save()
                print(sub.user, shared_amount, "=>", sale.conf.owner)
