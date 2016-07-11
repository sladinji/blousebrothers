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

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)

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
    university = models.ForeignKey('University', blank=True, null=True)
    """University"""


class University(models.Model):
    name = models.CharField(_("Nom"), max_length=128, blank=False, null=False)
    """University name"""
    city = models.CharField(_("Ville"), blank=True, null=True, max_length=50)
    """City"""

    def __str__(self):
        return self.name
admin.site.register(University)
