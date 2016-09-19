# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-19 15:36
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
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(blank=True, max_length=256, null=True, verbose_name='Proposition')),
                ('explaination', models.CharField(blank=True, max_length=256, null=True, verbose_name='Explication')),
                ('explaination_image', models.ImageField(blank=True, max_length=255, null=True, upload_to='images/products/%Y/%m/', verbose_name='Image')),
                ('correct', models.BooleanField(default=False, verbose_name='Correct')),
                ('ziw', models.BooleanField(default=False, verbose_name='Zéro si erreur')),
                ('index', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
            ],
        ),
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('title', models.CharField(max_length=64, verbose_name='Titre')),
                ('type', models.CharField(choices=[('DCP', 'DCP'), ('QI', 'QI')], default='DP', max_length=10, verbose_name='Type')),
                ('slug', oscar.models.fields.autoslugfield.AutoSlugField(blank=True, editable=False, max_length=128, populate_from='title', unique=True, verbose_name='Slug')),
                ('summary', models.CharField(help_text='Ce résumé doit décrire le contenu de la conférence en moins de 140 caractères.', max_length=140, verbose_name='Résumé')),
                ('statement', models.TextField(verbose_name='Énoncé')),
                ('edition_progress', models.PositiveIntegerField(default=0, verbose_name='Progression')),
            ],
        ),
        migrations.CreateModel(
            name='ConferenceImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=255, upload_to='images/products/%Y/%m/', verbose_name='Image')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Légende')),
                ('index', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('conf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='confs.Conference')),
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
                ('index', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('coefficient', models.PositiveIntegerField(default=1, verbose_name='Coéfficient')),
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
                ('index', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
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
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='confs.Question'),
        ),
    ]
