# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-21 15:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_import_cards'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='revision',
            field=models.BooleanField(default=False),
        ),
    ]
