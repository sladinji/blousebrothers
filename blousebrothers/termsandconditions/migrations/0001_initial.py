# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-23 11:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TermsAndConditions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default='site-terms')),
                ('name', models.TextField(max_length=255)),
                ('version_number', models.DecimalField(decimal_places=2, default=1.0, max_digits=6)),
                ('text', models.TextField(blank=True, null=True)),
                ('info', models.TextField(blank=True, help_text="Provide users with some info about what's changed and why", null=True)),
                ('date_active', models.DateTimeField(blank=True, help_text='Leave Null To Never Make Active', null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Terms and Conditions',
                'get_latest_by': 'date_active',
                'ordering': ['-date_active'],
                'verbose_name_plural': 'Terms and Conditions',
            },
        ),
        migrations.CreateModel(
            name='UserTermsAndConditions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')),
                ('date_accepted', models.DateTimeField(auto_now_add=True, verbose_name='Date Accepted')),
                ('terms', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userterms', to='termsandconditions.TermsAndConditions')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userterms', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Terms and Conditions',
                'get_latest_by': 'date_accepted',
                'verbose_name_plural': 'User Terms and Conditions',
            },
        ),
        migrations.AddField(
            model_name='termsandconditions',
            name='users',
            field=models.ManyToManyField(blank=True, through='termsandconditions.UserTermsAndConditions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='usertermsandconditions',
            unique_together=set([('user', 'terms')]),
        ),
    ]