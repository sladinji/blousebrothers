# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-25 09:02
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0005_auto_20161018_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, max_length=128, populate_from='title', unique=True, verbose_name='Slug'),
        ),
    ]