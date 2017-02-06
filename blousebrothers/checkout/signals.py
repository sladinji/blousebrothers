from datetime import date
from dateutil.relativedelta import relativedelta

from django.dispatch import receiver
from django.core.mail import send_mail
from django.apps import apps
from oscar.apps.checkout.signals import post_checkout

SubscriptionType = apps.get_model('confs', 'SubscriptionType')
Subscription = apps.get_model('confs', 'Subscription')


def handle_bonus(user, sub):
    bonus = user.handle_subscription_bonus(sub)
    if bonus:
        ctx = dict(bonus=bonus)
        msg_plain = render_to_string('confs/email/bonus.txt', ctx)
        msg_html = render_to_string('confs/email/bonus.html', ctx)
        send_mail(
                'Crédit BlouseBrothers',
                msg_plain,
                'noreply@blousebrothers.fr',
                [request.user.email],
                html_message=msg_html,
        )
    invitation = user.handle_sponsor_bonus(sub)
    if invitation:
        ctx = dict( sponsored=user,
                   sponsor=invitation.inviter,
                   bonus=sub.type.bonus_sponsor,
                   sub=sub,
                   )
        msg_plain = render_to_string('confs/email/bonus_sponsor.txt', ctx)
        msg_html = render_to_string('confs/email/bonus_sponsor.html', ctx)
        send_mail(
                'Bonus filleul',
                msg_plain,
                'noreply@blousebrothers.fr',
                [invitation.inviter.email],
                html_message=msg_html,
        )

@receiver(post_checkout)
def handle_subscription(sender, **kwargs):
    """
    Look for subscription to update user according to what was bought.
    """
    for line in kwargs['order'].lines.all():
        if 'abonnement' in line.product.product_class.name.lower():
            subtype, __ = SubscriptionType.objects.get_or_create(product=line.product)
            subtype.name = line.product.title
            subtype.description = line.product.description
            subtype.price = line.line_price_before_discounts_incl_tax
            subtype.bonus = line.product.attr.bonus
            subtype.bonus_sponsor = line.product.attr.bonus_sponsor
            subtype.save()
            sub = Subscription(user=line.order.user, type=subtype)
            sub.date_over = date.today() + relativedelta(months=+line.product.attr.month)
            sub.price_paid = line.unit_price_incl_tax
            sub.save()
            line.order.user.handle_subscription_bonus(sub)
            line.order.user.handle_sponsor_bonus(sub)
