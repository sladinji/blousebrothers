from django.core.management.base import BaseCommand
from django.contrib.flatpages.models import FlatPage
from termsandconditions.models import TermsAndConditions


class Command(BaseCommand):
    help = 'Sync cgu accept content wit /CGU'


    def handle(self, *args, **options):
        cgu = TermsAndConditions.objects.last()
        cgu.text = FlatPage.objects.get(title='CGU-CGV').content
        cgu.save()
