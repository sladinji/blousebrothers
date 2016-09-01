# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-01 14:32
from __future__ import unicode_literals

import blousebrothers.users.models
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import shortuuidfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.')], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Prénom Nom')),
                ('sponsor_code', models.CharField(default=blousebrothers.users.models.User.gen_sponsor_code, max_length=8, unique=True, verbose_name='Code Parrain')),
                ('uuid', shortuuidfield.fields.ShortUUIDField(blank=True, db_index=True, editable=False, max_length=22, unique=True)),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Date de naissance')),
                ('address1', models.CharField(blank=True, max_length=50, null=True, verbose_name='Adresse 1')),
                ('address2', models.CharField(blank=True, max_length=50, verbose_name='Adresse 2')),
                ('city', models.CharField(blank=True, max_length=50, null=True, verbose_name='Ville')),
                ('zip_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='Code postal')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Fixe')),
                ('mobile', models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Mobile')),
                ('is_conferencier', models.BooleanField(default=False, verbose_name='Conférencier')),
                ('is_patriot', models.BooleanField(default=False, verbose_name='Conférencier')),
                ('university', models.CharField(blank=True, choices=[('aix-marseille', 'Aix-Marseille'), ('amiens', 'Amiens'), ('angers', 'Angers'), ('antilles-guya', 'Antilles-Guyane'), ('besancon', 'Besançon'), ('bordeaux_2', 'Bordeaux 2'), ('brest', 'Brest'), ('caen', 'Caen'), ('clermont_ferr', 'Clermont Ferrand 1'), ('corse', 'Corse'), ('dijon', 'Dijon'), ('grenoble_1', 'Grenoble 1'), ('la_reunion', 'La Réunion'), ('lille_2', 'Lille 2'), ('limoge', 'Limoge'), ('lorraine', 'Lorraine'), ('lyon_1', 'Lyon 1'), ('montpellier_1', 'Montpellier 1'), ('nantes', 'Nantes'), ('nice', 'Nice'), ('paris_11', 'Paris 11'), ('paris_12', 'Paris 12'), ('paris_13', 'Paris 13'), ('paris_5', 'Paris 5'), ('paris_6', 'Paris 6'), ('paris_7', 'Paris 7'), ('poitiers', 'Poitiers'), ('reims', 'Reims'), ('rennes_1', 'Rennes 1'), ('rouen', 'Rouen'), ('st-etienne', 'Saint-Etienne'), ('strasbourg', 'Strasbourg'), ('toulouse_3', 'Toulouse 3'), ('tours', 'Tours'), ('versailles_st', 'Versailles Saint-Quentin-en-Yveline'), ('x', 'Autre...')], max_length=15, null=True, verbose_name='Université')),
                ('degree', models.CharField(choices=[('P2', 'P2'), ('P3', 'P3'), ('M1', 'M1'), ('M2', 'M2'), ('M3', 'M3'), ('INTERNE', 'Interne'), ('MEDECIN', 'Médecin')], default=None, max_length=10, null=True, verbose_name='Niveau')),
                ('friends', models.ManyToManyField(related_name='_user_friends_+', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('sponsor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'abstract': False,
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
