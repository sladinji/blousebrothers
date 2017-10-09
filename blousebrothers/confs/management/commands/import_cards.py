from glob import glob
from django.core.management.base import BaseCommand
from blousebrothers.cards.loader import text
from blousebrothers.users.models import User


class Command(BaseCommand):
    help = 'Import .md cards in fiches folder'

    def handle(self, *args, **options):
        user = User.objects.get(username="BlouseBrothers")
        for fn in glob('fiches/*'):
            with open(fn, 'rb') as fd:
                print(">> importing %s" % fn)
                text.load(fd, user)
