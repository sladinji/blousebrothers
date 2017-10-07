
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from blousebrothers.users.models import User
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Send email to user if new cards are ready to learn'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('username', nargs='*')

    def go(self, qs):
        now = timezone.now()
        for user in qs.all():
            card_ready_qry = user.deck.filter(wake_up__gt=now-timedelta(days=1), wake_up__lt=now)
            nb_new_cards_ready = card_ready_qry.count()
            if not nb_new_cards_ready:
                continue
            print("{} has {} to learn.".format(user, nb_new_cards_ready))
            ctx = {'previews': [x.card.content.split('\n')[0].replace("@", "")
                                for x in card_ready_qry[:10]
                                ],
                   'nb_new_cards_ready': nb_new_cards_ready,
                   'user': user,
                   }

            msg_plain = render_to_string('cards/emails/ready_to_learn.txt', ctx)
            msg_html = render_to_string('cards/emails/ready_to_learn.html', ctx)
            email = EmailMultiAlternatives(
                "Nouvelles fiches prêtes à revoir",
                msg_plain,
                '<BlouseBrothers noreply@blousebrothers.fr>',
                [user.email],
            )
            email.attach_alternative(msg_html, "text/html")
            email.extra_headers['X-Mailgun-Tag'] = ['RelanceFiches']
            email.send()

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
                    self.go(qs)
            else:
                self.go(User.objects)
        except Exception:
                sentry.captureException()
