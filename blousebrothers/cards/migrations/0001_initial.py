# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-17 11:35
from __future__ import unicode_literals

import blousebrothers.confs.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('confs', '0050_auto_20170712_1345'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(max_length=256, verbose_name='Chapitre')),
                ('title', models.CharField(max_length=256, verbose_name='Titre du cours')),
                ('content', models.TextField(blank=True, null=True, verbose_name='Contenu')),
                ('slug', blousebrothers.confs.models.AutoSlugField(editable=False, max_length=256, populate_from='content', unique=True, verbose_name='Slug')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_cards', to=settings.AUTH_USER_MODEL, verbose_name='Auteur')),
                ('items', models.ManyToManyField(blank=True, related_name='cards', to='confs.Item', verbose_name='Items')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='childs', to='cards.Card', verbose_name='Original')),
                ('specialities', models.ManyToManyField(blank=True, related_name='cards', to='confs.Speciality', verbose_name='Specialities')),
            ],
        ),
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.PositiveIntegerField(default=1, verbose_name='Difficulté')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classeur', to='cards.Card', verbose_name='Fiche')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classeur', to=settings.AUTH_USER_MODEL, verbose_name='Étudiant')),
            ],
        ),
    ]
