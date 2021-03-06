# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-15 12:35
from __future__ import unicode_literals

import blousebrothers.confs.models
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0029_auto_20161212_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionExplainationImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', image_cropping.fields.ImageCropField(max_length=255, upload_to=blousebrothers.confs.models.question_image_directory_path, verbose_name='Image')),
                ('cropping', image_cropping.fields.ImageRatioField('image', '430x360', adapt_rotation=False, allow_fullsize=False, free_crop=True, help_text=None, hide_image_field=False, size_warning=False, verbose_name='cropping')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Libellé')),
                ('index', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='explaination_images', to='confs.Question')),
            ],
        ),
        migrations.AlterField(
            model_name='conference',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.5'), help_text='', max_digits=6, verbose_name='Prix de vente'),
        ),
    ]
