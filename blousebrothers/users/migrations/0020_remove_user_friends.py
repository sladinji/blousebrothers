# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-09-25 10:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_user_last_last_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='friends',
        ),
    ]
