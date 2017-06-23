from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils.six.moves import input

from blousebrothers.users.models import User, Sale

PRICE = Decimal("9")


def boolean_input(question, default=None):
    result = input("%s " % question)
    if not result and default is not None:
        return default
    while len(result) < 1 or result[0].lower() not in "yn":
        result = input("Please answer yes or no: ")
    return result[0].lower() == "y"


class Command(BaseCommand):
    help = 'Pay conferenciers according to on going subscriptions'

    def handle(self, *args, **options):
        subscribers = User.objects.filter(subs__price_paid=0).count()
        credit = PRICE * subscribers * Decimal('0.7')
        credit = credit.quantize(Decimal('1.00'))  # arrondi
        benef = PRICE * subscribers * Decimal('0.3')
        benef = benef.quantize(Decimal('1.00'))  # arrondi
        sales_count = Sale.objects.filter(credited_funds=0).count()
        print("Cadeaux D4 : {subscribers} x 9€ * 70% = {credit:f}€ \nBenef (futur...): {benef:f}€".format(
            credit=credit, benef=benef, subscribers=subscribers)
        )
        unit_price = Decimal(credit) / sales_count * Decimal('0.7')
        unit_price = unit_price.quantize(Decimal('1.00'))  # arrondi
        print("Soit ", unit_price, "€ par vente")
        if not boolean_input("Go ?"):
            return

        for sale in Sale.objects.filter(
            credited_funds=0
        ).values(
            'conf__owner'
        ).annotate(
            total=Count('conf')
        ).order_by('-total'):
            amount = unit_price*sale['total']
            amount = amount.quantize(Decimal('1.00'))  # arrondi
            user = User.objects.get(pk=sale['conf__owner'])
            print('{} soit {:f} € pour {}'.format(
                sale['total'],
                amount,
                user.username)
            )
            user.credit_wallet(unit_price*sale['total'])
            for sale in Sale.objects.filter(credited_funds=0, conf__owner=user):
                sale.credited_funds = unit_price
                sale.save()
