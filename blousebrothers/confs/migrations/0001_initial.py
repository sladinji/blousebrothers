# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-05 12:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import oscar.models.fields.autoslugfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('title', models.CharField(max_length=64, verbose_name='Titre')),
                ('slug', oscar.models.fields.autoslugfield.AutoSlugField(blank=True, editable=False, max_length=128, populate_from='title', unique=True, verbose_name='Slug')),
                ('abstract', models.TextField(verbose_name='Résumé')),
                ('type', models.CharField(choices=[('QI', 'QI'), ('DCP', 'DCP')], default='QI', max_length=10, verbose_name='Type')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Item')),
                ('number', models.IntegerField(verbose_name='Numéro')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(max_length=64, verbose_name='Enoncé')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('answer_a', models.CharField(max_length=256, verbose_name='Réponse A')),
                ('explaination_a', models.CharField(blank=True, max_length=256, null=True, verbose_name='Explication')),
                ('correct_a', models.BooleanField(default=False, verbose_name='Correct')),
                ('answer_b', models.CharField(max_length=256, verbose_name='Réponse B')),
                ('explaination_b', models.CharField(blank=True, max_length=256, null=True, verbose_name='Explication')),
                ('correct_b', models.BooleanField(default=False, verbose_name='Correct')),
                ('answer_c', models.CharField(max_length=256, verbose_name='Réponse C')),
                ('explaination_c', models.CharField(blank=True, max_length=256, null=True, verbose_name='Explication')),
                ('correct_c', models.BooleanField(default=False, verbose_name='Correct')),
                ('answer_d', models.CharField(max_length=256, verbose_name='Réponse D')),
                ('explaination_d', models.CharField(blank=True, max_length=256, null=True, verbose_name='Explication')),
                ('correct_d', models.BooleanField(default=False, verbose_name='Correct')),
                ('answer_e', models.CharField(max_length=256, verbose_name='Réponse E')),
                ('explaination_e', models.CharField(blank=True, max_length=256, null=True, verbose_name='Explication')),
                ('correct_e', models.BooleanField(default=False, verbose_name='Correct')),
                ('conf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='confs.Conference', verbose_name='Conference')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=255, upload_to='images/products/%Y/%m/', verbose_name='Image')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Libellé')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='confs.Question')),
            ],
        ),
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Matière')),
            ],
        ),
        migrations.AddField(
            model_name='conference',
            name='items',
            field=models.ManyToManyField(related_name='conferences', to='confs.Item', verbose_name='Items'),
        ),
        migrations.AddField(
            model_name='conference',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conference',
            name='specialities',
            field=models.ManyToManyField(related_name='conferences', to='confs.Speciality', verbose_name='Spécialités'),
        ),
    ]
