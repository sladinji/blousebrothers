# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from shortuuidfield import ShortUUIDField
from django.contrib import admin


@python_2_unicode_compatible
class User(AbstractUser):

    DEGREE_LEVEL = (
        ('P2', _('P2')),
        ('P3', _('P3')),
        ('M1', _('M1')),
        ('M2', _('M2')),
        ('M3', _('M3')),
        ('INTERNE', _('Interne')),
        ('MEDECIN', _('Médecin')),
    )
    UNIVERSITY = (('aix-marseille', 'Aix-Marseille'),
      ('amiens', 'Amiens'),
      ('angers', 'Angers'),
      ('antilles-guya', 'Antilles-Guyane'),
      ('besancon', 'Besançon'),
      ('bordeaux_2', 'Bordeaux 2'),
      ('brest', 'Brest'),
      ('caen', 'Caen'),
      ('clermont_ferr', 'Clermont Ferrand 1'),
      ('corse', 'Corse'),
      ('dijon', 'Dijon'),
      ('grenoble_1', 'Grenoble 1'),
      ('la_reunion', 'La Réunion'),
      ('lille_2', 'Lille 2'),
      ('limoge', 'Limoge'),
      ('lorraine', 'Lorraine'),
      ('lyon_1', 'Lyon 1'),
      ('montpellier_1', 'Montpellier 1'),
      ('nantes', 'Nantes'),
      ('nice', 'Nice'),
      ('paris_11', 'Paris 11'),
      ('paris_12', 'Paris 12'),
      ('paris_13', 'Paris 13'),
      ('paris_5', 'Paris 5'),
      ('paris_6', 'Paris 6'),
      ('paris_7', 'Paris 7'),
      ('poitiers', 'Poitiers'),
      ('reims', 'Reims'),
      ('rennes_1', 'Rennes 1'),
      ('rouen', 'Rouen'),
      ('st-etienne', 'Saint-Etienne'),
      ('strasbourg', 'Strasbourg'),
      ('toulouse_3', 'Toulouse 3'),
      ('tours', 'Tours'),
      ('versailles_st', 'Versailles Saint-Quentin-en-Yveline'),
      ('x', 'Autre...'),)


    def gen_sponsor_code():
        """
        Return a unique 8 numbers codes for user. Used as function to generate default value.
        """
        random_number = User.objects.make_random_password(length=8, allowed_chars='123456789')
        while User.objects.filter(sponsor_code=random_number):
                random_number = User.objects.make_random_password(length=8, allowed_chars='123456789')
        return random_number

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    """Comes from cookie cutter.import..."""
    sponsor_code = models.CharField(_("Code Parrain"), max_length=8, default=gen_sponsor_code, unique=True)
    """Code referencing that user in case of sponsorship"""
    sponsor = models.ForeignKey('self', null=True, blank=True)
    """Reference to the sponsor user"""
    uuid = ShortUUIDField(unique=True, db_index=True)
    """UUID than can be used in public link to identify user"""
    birth_date = models.DateField(_("Date de naissance"), blank=True, null=True)
    """Birth date."""
    address1 = models.CharField(_("Adresse 1"), blank=True, null=True, max_length=50)
    """Address first line"""
    address2 = models.CharField(_("Adresse 2"), blank=True, max_length=50)
    """Address second line"""
    city = models.CharField(_("Ville"), blank=True, null=True, max_length=50)
    """City"""
    zip_code = models.CharField(_("Code postal"), blank=True, null=True, max_length=20)
    """ Zip code"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. "
                  "Up to 15 digits allowed.")
    )
    """ Phone regex validator """
    phone = models.CharField(_("Fixe"), validators=[phone_regex], blank=True, null=True,
                             max_length=20
                             )
    """Phone number"""
    mobile = models.CharField(_("Mobile"), validators=[phone_regex], blank=True, max_length=20)
    """Mobile phone number"""
    is_conferencier = models.BooleanField("Conférencier", default=False)
    """Is user a "conferencier" or not"""
    is_patriot = models.BooleanField("Conférencier", default=False)
    """Patriot will offer free stuff to students of his university"""
    university = models.CharField(_('Université'), max_length=15, blank=False, null=True,
                                  choices=UNIVERSITY)
    """University"""
    degree = models.CharField(_("Niveau"), max_length=10, choices=DEGREE_LEVEL,
                            blank=False, default=None, null=True)
    """Degree level"""
    friends = models.ManyToManyField('self')
    """Friends"""

    def gave_all_required_info(self):
        """Used for permission management"""
        return self.university and self.first_name and self.last_name and self.degree

