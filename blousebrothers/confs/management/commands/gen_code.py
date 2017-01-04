import csv
import codecs
from urllib.request import urlopen
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from oscar.core.loading import get_class, get_classes

Range, Condition, ConditionalOffer, Benefit, = get_classes(
    'offer.models', ("Range", "Condition", "ConditionalOffer", "Benefit"))
Voucher = get_class('voucher.models', 'Voucher')


def create_promo(
    type='Absolute',
    value=15,
    name='Offre de lancement',
    code='CODETEST',
    start_datetime='03/01/2017 12:30:46',
    usage='Single use'
):
    range, __ = Range.objects.get_or_create(name="Abonnements")

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

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        data = urlopen(options['url'])
        decoder = codecs.getreader("utf-8")
        reader = csv.DictReader(decoder(data))

        with open("code.csv", "w") as out:
            writer = csv.DictWriter(out, reader.fieldnames + ['CODE15EUR'])
            writer.writeheader()
            for row in reader:
                code = "Just-4-" + row['Email'].split('@')[0]
                try:
                    create_promo(code=code)
                except IntegrityError as err:
                    self.stdout.write(self.style.ERROR(err))
                writer.writerow(dict(CODE15EUR=code, **row))
