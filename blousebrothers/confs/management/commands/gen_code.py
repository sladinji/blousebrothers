from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from oscar.core.loading import get_class, get_classes
Range, Condition, ConditionalOffer, Benefit, Offer, = get_classes(
    'offer.models', ("Range", "Condition", "ConditionalOffer", "Benefit", "Offer", ))
Voucher = get_class('catalogue.models', 'Voucher')


def create_promo(
    range=Range.objects.get(name="Abonnements"),
    type='Absolute',
    value=15,
    name='Offre de lancement',
    code='CODETEST',
    start_datetime='03/01/2017 12:30:46',
    usage='Single use'
):

    start_datetime = datetime.strptime(start_datetime, "%d/%m/%Y %H:%M:%S")
    condition = Condition.objects.create(
        range=range,
        type=Condition.COUNT,
        value=1
    )
    benefit = Benefit.objects.create(
        range=range,
        type=type,
        value=value,
    )
    offer = ConditionalOffer.objects.create(
        name="Promo pour '%s'" % code,
        offer_type=ConditionalOffer.VOUCHER,
        benefit=benefit,
        condition=condition,
    )
    voucher, __ = Voucher.objects.get_or_create(
        name=name,
        code=code,
        usage=usage,
        start_datetime=start_datetime,
        end_datetime=start_datetime + timedelta(days=60),
    )
    voucher.offers.add(offer)


class Command(BaseCommand):
	help = "Create code promo abonnement 15 euros"

	def handle(self, *args, **options):
		create_promo(**options)

