
from django.core.management.base import BaseCommand
from blousebrothers import mailchimp
from blousebrothers.users.models import User


class Command(BaseCommand):
    help = 'Mailchimp blousebrothers list synchronization'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('username', nargs='*')

    def handle(self, *args, **options):
        if options['username']:
            qs = User.objects.filter(username__in=options['username']).all()
            if not qs:
                print("User not found")
                return
            else:
                print("{} user(s) found".format(qs.count()))
                mailchimp.sync(qs)
        else:
            mailchimp.sync()
