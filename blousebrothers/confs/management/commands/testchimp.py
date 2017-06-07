from django.core.management.base import BaseCommand
from blousebrothers import mailchimp
import hashlib


class Command(BaseCommand):
    help = 'Mailchimp test'

    def add_arguments(self, parser):
        parser.add_argument('--email', nargs='?', default='julien.almarcha@gmail.com')
        for tag in mailchimp.tags.keys():
            parser.add_argument('--' + tag, nargs='?')

    def handle(self, *args, **options):
        email = options.pop('email')
        merge_fields = {mailchimp.tags[k]: v for k,v in options.items() if v and k in mailchimp.tags}
        print(email)
        print(merge_fields)
        mailchimp.client.lists.members.create_or_update(
            mailchimp.mc_lids[mailchimp.LIST_NAME],
            subscriber_hash=hashlib.md5(email.lower().encode()).hexdigest(),
            data={
                'email_address': email,
                'status_if_new': 'subscribed',
                'merge_fields': merge_fields,
            })
