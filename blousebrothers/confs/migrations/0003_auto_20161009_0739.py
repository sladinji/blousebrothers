# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-09 07:39
from __future__ import unicode_literals

import blousebrothers.confs.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0002_auto_20160920_1131'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemKeyWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=128, verbose_name='Valeur')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kwords', to='confs.Item')),
            ],
        ),
        migrations.AlterField(
            model_name='answer',
            name='explaination_image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=blousebrothers.confs.models.answer_image_directory_path, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='items',
            field=models.ManyToManyField(help_text='Ne sélectionnez que les items abordés de manière <strong>significative</strong> dans votre dossier', related_name='conferences', to='confs.Item', verbose_name='Items'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='statement',
            field=models.TextField(blank=True, null=True, verbose_name='Énoncé*'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='summary',
            field=models.CharField(help_text='Ex: "dossier très pointu et monothématique sur la fibrillation auriculaire" ou "dossier transversal de révisions classiques sur lupus et grossesse" ', max_length=140, verbose_name='Esprit du dossier'),
        ),
        migrations.AlterField(
            model_name='conferenceimage',
            name='image',
            field=models.ImageField(max_length=255, upload_to=blousebrothers.confs.models.conf_directory_path, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='questionimage',
            name='image',
            field=models.ImageField(max_length=255, upload_to=blousebrothers.confs.models.question_image_directory_path, verbose_name='Image'),
        ),
    ]
