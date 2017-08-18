import numpy as np

from django.core.management.base import BaseCommand
from oscar.core.loading import get_classes


StatsSpe, StatsItem, Test, Speciality, Item = get_classes('confs.models', ("StatsSpe", "StatsItem", "Test", "Speciality", "Item"))


class Command(BaseCommand):
    help = 'Evaluate new stats for all specialies and items'

    def handle(self, *args, **options):
        for spe in Speciality.objects.all():
            stats = StatsSpe.objects.get_or_create(speciality=spe)[0]
            l = [
                test.score for test
                in Test.objects.filter(conf__specialities__in=[spe], finished=True).all()
            ]
            l = l if l != [] else [0]
            stats.average = np.mean(l)
            stats.median = np.median(l)
            stats.std_dev = np.std(l)
            stats.save()

        for item in Item.objects.all():
            stats = StatsSpe.objects.get_or_create(item=item)[0]
            l = [
                test.score for test
                in Test.objects.filter(conf__item__in=[item], finished=True).all()
            ]
            l = l if l != [] else [0]
            stats.average = np.mean(l)
            stats.median = np.median(l)
            stats.std_dec = np.std(l)
            stats.save()
