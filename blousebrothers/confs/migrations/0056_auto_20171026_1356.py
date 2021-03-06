# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-10-26 13:56
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0055_auto_20171016_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='correction_dispo',
            field=models.BooleanField(default=True, help_text="Désactive l'accès à la correction si tu fais une correction en présentiel. N'oublie pas de le ré-activer après !", verbose_name='Correction accessible'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='for_sale',
            field=models.BooleanField(default=True, help_text="Publier mon dossier avec les paramètres sélectionnés. Je certifie que le matériel de ma conférence est original et je dégage BlouseBrothers de toute responsabilité concernant son contenu. Je suis au courant de mes obligations en matière de fiscalité, détaillées dans les <a href='/cgu/'>conditions générales d'utilisation</a>.", verbose_name='Accessible à tous'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='for_share',
            field=models.BooleanField(default=True, help_text="Le dossier est accessible aux personnes autorisées dans la section <a href='/amis'>Amis</a>, même si le dossier n'est pas accessible publiquement.", verbose_name='Accessible à mes élèves / amis'),
        ),
        migrations.AlterField(
            model_name='conference',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('1'), help_text='', max_digits=6, verbose_name='Prix de vente'),
        ),
    ]
