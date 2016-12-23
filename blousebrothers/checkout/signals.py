from datetime import date

from dateutil.relativedelta import relativedelta
from django.dispatch import receiver
from django.apps import apps
from oscar.apps.checkout.signals import post_checkout

SubscriptionType = apps.get_model('confs', 'SubscriptionType')
Subscription = apps.get_model('confs', 'Subscription')


@receiver(post_checkout)
def handle_subscription(sender, **kwargs):
    """
    Look for subscription to update user according to what was bought.
    """
    for line in kwargs['order'].lines.all():
        if 'abonnement' in line.product.product_class.name.lower():
            subtype, __ = SubscriptionType.objects.get_or_create(
                name=line.product.title,
                description=line.product.description,
                price=line.line_price_before_discounts_incl_tax,
            )
            sub = Subscription(
                user=line.order.user,
                type=subtype,
            )
            sub.date_over = date.today() + relativedelta(months=+line.product.attr.month)
            sub.price_paid = line.unit_price_incl_tax
            sub.save()
