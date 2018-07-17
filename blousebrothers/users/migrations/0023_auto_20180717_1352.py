# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-17 13:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20180716_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='sponsor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='university',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.University', verbose_name='Ville de CHU actuelle'),
        ),
    ]
