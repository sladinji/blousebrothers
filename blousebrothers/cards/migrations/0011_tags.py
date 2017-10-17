# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def update_items(apps, schema_editor):
    """
    Add card's items according to card's tags.
    """
    Card = apps.get_model('cards', 'Card')
    Item = apps.get_model('confs', 'Item')

    for x in range(400):
        for card in Card.objects.filter(tags__name=str(x)):
            card.items.add(Item.objects.get(number=x))
            card.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0010_cardimage'),
    ]

    operations = [
        migrations.RunPython(update_items),
    ]
