# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-05-12 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20170411_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(default='registered', max_length=50, null=True, verbose_name='Status'),
        ),
    ]