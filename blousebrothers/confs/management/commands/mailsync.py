from django.core.management.base import BaseCommand
from blousebrothers import mailchimp
from blousebrothers.users.models import User


class Command(BaseCommand):
    help = 'Mailchimp blousebrothers list synchronization'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('username', nargs='*')

    def handle(self, *args, **options):
        from raven import Client
        sentry = Client('https://770aeeaa5cc24a3e8b16a10c328c28c5:1aca22596ba1421198ff5269032f0ffd@sentry.io/104798')
        try:
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
        except Exception:
                sentry.captureException()
