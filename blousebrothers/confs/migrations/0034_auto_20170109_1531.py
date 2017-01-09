# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-09 15:31
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0033_auto_20170102_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.5'), help_text='', max_digits=6, verbose_name='Prix de vente'),
        ),
    ]
