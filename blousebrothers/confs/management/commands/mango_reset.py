from django.core.management.base import BaseCommand
from oscar.core.loading import get_classes


MangoPayUser, = get_classes('mangopay.models', ('MangoPayUser',))


class Command(BaseCommand):
    help = 'Delete MangoPayUsers'

    def handle(self, *args, **options):
        resp = MangoPayUser.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("MangoPayUser reset success : {}".format(resp)))
