# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-16 15:04
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0056_auto_20171026_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('1'), help_text='', max_digits=6, verbose_name='Prix de vente'),
        ),
    ]
