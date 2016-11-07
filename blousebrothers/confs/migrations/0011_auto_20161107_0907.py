# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-07 09:07
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('confs', '0010_auto_20161031_1558'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('progress', models.PositiveIntegerField(default=0, verbose_name='Progression')),
                ('result', models.PositiveIntegerField(default=0, verbose_name='Résultat')),
                ('max_score', models.PositiveIntegerField(default=0, verbose_name='Résultat')),
                ('score', models.PositiveIntegerField(default=0, verbose_name='Résultat')),
                ('finished', models.BooleanField(default=False)),
                ('personal_note', models.TextField(blank=True, help_text='Visible uniquement par toi, note ici les choses que tu veux retenir, ça pourra également te permettre de retrouver plus facilement ce dossier.', null=True, verbose_name='Remarques personnelles')),
                ('date_started', models.DateTimeField(auto_now_add=True, verbose_name='Début du test')),
                ('date_finished', models.DateTimeField(default=None, verbose_name='Fin du test')),
                ('time_taken', models.TimeField(verbose_name='Temps passé')),
            ],
        ),
        migrations.CreateModel(
            name='TestAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_started', models.DateTimeField(auto_now_add=True, verbose_name='Début')),
                ('date_finished', models.DateTimeField(default=None, verbose_name='Fin')),
                ('time_taken', models.TimeField(default=0, verbose_name='Temps passé')),
                ('given_answers', models.CharField(blank=True, max_length=30, verbose_name='Réponses')),
                ('max_score', models.PositiveIntegerField(default=0, verbose_name='Résultat')),
                ('score', models.PositiveIntegerField(default=0, verbose_name='Résultat')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_answers', to='confs.Question')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='confs.Test')),
            ],
        ),
        migrations.AddField(
            model_name='conferenceimage',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('image', '1430x1360', adapt_rotation=False, allow_fullsize=False, free_crop=False, help_text=None, hide_image_field=False, size_warning=False, verbose_name='cropping'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='for_sale',
            field=models.BooleanField(default=False, help_text='Un sujet accessible apparaitra dans les recherches et pourra être acheté au prix que vous avez fixé.', verbose_name='Accessible'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_confs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='conference',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.5'), help_text='', max_digits=6, verbose_name='Prix de vente'),
        ),
        migrations.AddField(
            model_name='test',
            name='conf',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='confs.Conference'),
        ),
        migrations.AddField(
            model_name='test',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to=settings.AUTH_USER_MODEL),
        ),
    ]