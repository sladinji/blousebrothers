# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-27 15:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_auto_20170727_1515'),
        ('users', '0016_auto_20170726_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cards',
            field=models.ManyToManyField(related_name='students', through='cards.Deck', to='cards.Card'),
        ),
    ]
