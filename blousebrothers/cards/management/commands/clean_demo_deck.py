import datetime

from django.core.management.base import BaseCommand

from blousebrothers.users.models import User


class Command(BaseCommand):
    help = 'Remove demo deck cards older than 3 days'

    def handle(self, *args, **options):
        deletions = User.objects.get(
            username="demo"
        ).deck.filter(
            created__lt=datetime.datetime.today() - datetime.timedelta(days=3)
        ).delete()
        print("{} cards deleted".format(deletions))
