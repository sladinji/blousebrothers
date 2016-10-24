# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-18 13:52
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0004_auto_20161018_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='conference',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.5'), help_text="Une commission de 10% du prix de vente + 10 centimes est soustraite à chaque vente réalisée. <a href='/cgu'>Voir nos conditions générales d'utilisation</a>.", max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.5')), django.core.validators.MaxValueValidator(100)], verbose_name='Prix de vente'),
        ),
    ]