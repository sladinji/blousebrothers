from glob import glob
from django.core.management.base import BaseCommand
from blousebrothers.users.models import User
from blousebrothers.cards.models import Card
from blousebrothers.cards.loader import load_apkg


class Command(BaseCommand):
    help = 'Import .md cards in fiches folder'

    def add_arguments(self, parser):
        # This is an optional argument
        parser.add_argument('reset', nargs='*', type=str)

    def handle(self, *args, **options):
        if "reset" in options['reset']:
            if input("Reset ? N/y") == 'y':
                Card.objects.all().delete()
        user = User.objects.get(username="BlouseBrothers")
        for fn in glob('apkgs/*'):
            with open(fn, "rb") as fd:
                load_apkg(fd, user)
