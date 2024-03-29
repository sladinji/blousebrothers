# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-21 13:54
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('confs', '0030_auto_20161215_1235'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_over', models.DateTimeField(verbose_name='Date created')),
                ('price_paid', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Vendu pour')),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Nom')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('nb_month', models.IntegerField(blank=True, null=True, verbose_name='Durée')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Prix')),
            ],
        ),
        migrations.AlterField(
            model_name='conference',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.5'), help_text='', max_digits=6, verbose_name='Prix de vente'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subs', to='confs.SubscriptionType'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subs', to=settings.AUTH_USER_MODEL),
        ),
    ]
