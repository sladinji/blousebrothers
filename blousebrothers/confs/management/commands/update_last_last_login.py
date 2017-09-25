from django.core.management.base import BaseCommand

from django.db.models import F
from blousebrothers.users.models import User


class Command(BaseCommand):
    help = 'Evaluate new stats for all specialies and items'

    def handle(self, *args, **options):
        print(User.objects.update(last_last_login=F('last_login')))
