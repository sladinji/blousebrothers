
from django.core.management.base import BaseCommand
from blousebrothers import mailchimp


class Command(BaseCommand):
    help = 'Mailchimp blousebrothers list synchronization'

    def handle(self, *args, **options):
        mailchimp.sync()
