# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.db import migrations


def delete_orders(apps, schema_editor):
    """ Delete orders before subscriptions (must be pre delete action somewhere in all this import...)"""
    from oscar.apps.order.models import BillingAddress, CommunicationEvent, Line, LineAttribute, LinePrice, Order, OrderDiscount, OrderNote, PaymentEvent, PaymentEventType, ShippingAddress, ShippingEvent, ShippingEventType
    from oscar.apps.payment.models import Bankcard, Source, SourceType, Transaction

    Order.objects.filter(date_placed__lt=datetime.date(2017, 7, 5)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0053_codes_promo'),
    ]

    operations = [
        migrations.RunPython(delete_orders),
    ]
