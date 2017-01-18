# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.core.mail import mail_admins
from django_countries.fields import CountryField

from djmoney.models.fields import MoneyField
from allauth.account.signals import user_signed_up
from shortuuidfield import ShortUUIDField

from mangopay.models import (
    MangoPayNaturalUser,
    MangoPayWallet,
    MangoPayTransfer,
)
from blousebrothers.catalogue.models import Product

AbstractUser._meta.get_field('first_name').blank = False
AbstractUser._meta.get_field('last_name').blank = False
AbstractUser._meta.get_field('email').blank = False


@python_2_unicode_compatible
class User(AbstractUser):

    DEGREE_LEVEL = (
        (None, '---'),
        ('P1', _('P1')),
        ('P2', _('P2')),
        ('P3', _('P3')),
        ('M1', _('M1')),
        ('M2', _('M2')),
        ('M3', _('M3')),
        ('INTERNE', _('Interne')),
        ('MEDECIN', _('Médecin')),
    )

    def has_valid_subscription(self):
        return [x for x in self.subs.all() if not x.is_past_due]

    def already_done(self, conf):
        return self.tests.filter(conf=conf)

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
    birth_date = models.DateField(_("Date de naissance"), blank=False, null=True)
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
    is_conferencier = models.BooleanField(_("Conférencier"), default=False)
    """Is user a "conferencier" or not"""
    wanabe_conferencier = models.BooleanField(_("Souhaite devenir conférencier"), default=False)
    """Does user want to be a "conferencier" or not"""
    wanabe_conferencier_date = models.DateField(_("Date de demande"), blank=True, null=True)
    """Date when request to be conferencier was made"""
    is_patriot = models.BooleanField("Conférencier", default=False)
    """Patriot will offer free stuff to students of his university"""
    university = models.ForeignKey('University', blank=False, null=True, verbose_name=_("Ville de CHU actuelle"))
    """University"""
    degree = models.CharField(_("Niveau"), max_length=10, choices=DEGREE_LEVEL,
                              blank=False, default=None, null=True)
    """Degree level"""
    friends = models.ManyToManyField('self')
    """Friends"""
    country_of_residence = CountryField(_("Pays de résidence"), default="FR", blank=False)
    nationality = CountryField(_("Nationalité"), default="FR", blank=False)
    speciality = models.CharField(_("Spécialité"), max_length=128, blank=True, null=True)
    bio = models.TextField(_("Bio visible par les utilisateurs"),
                           blank=True, null=True,
                           help_text=_("Important si tu es conférencier !"),
                           )


    def gave_all_required_info(self):
        """Used for permission management"""
        if self.is_superuser:
            return True
        if self.wanabe_conferencier or self.is_conferencier:
            return self.university and self.first_name and self.last_name and self.degree
        return True

    def gave_all_mangopay_info(self):
        return self.birth_date and self.country_of_residence and self.nationality \
            and self.first_name and self.last_name

    @property
    def mangopay_user(self):

        mp_user, mpu_created = MangoPayNaturalUser.objects.get_or_create(user=self)
        if mpu_created:
            mp_user.birthday = self.birth_date
            mp_user.country_of_residence = self.country_of_residence
            mp_user.nationality = self.nationality
            mp_user.create()
        return mp_user

    @property
    def has_more_than_one_card(self):
        return len([x for x in self.mangopay_user.mangopay_card_registrations.all()
                    if x.mangopay_card.mangopay_id]) > 1

    @property
    def wallet(self):
        wallet, w_created = MangoPayWallet.objects.get_or_create(mangopay_user=self.mangopay_user)
        if w_created:
            wallet.mangopay_user = self.mangopay_user
            wallet.create(description="{}'s Wallet".format(self.username))
        return wallet


class Transaction(models.Model):
    conferencier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sells')
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transfer = models.ForeignKey(MangoPayTransfer, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    credited_funds = MoneyField(default=0, default_currency="EUR",
                                decimal_places=2, max_digits=12)
    fees = MoneyField(default=0, default_currency="EUR",
                      decimal_places=2, max_digits=12)
    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)


class University(models.Model):
    class Meta:
            ordering = ["name"]
    name = models.CharField(_("Nom"), max_length=128, blank=False, null=False)
    """University name"""

    def __str__(self):
        return self.name

email_template = '''
Nom : {}
Email : {}
Lien : {}{}{}'''


@receiver(user_signed_up, dispatch_uid="notify_signup")
def notify_signup(request, user, **kwargs):
    """
    send a mail to admin
    """
    msg = email_template.format(user.name,
                                user.email,
                                'https://' if request.is_secure() else 'http://',
                                request.get_host(),
                                reverse('admin:users_user_change',
                                        args=(user.id,)
                                        )
                                )
    mail_admins('Nouvelle inscription', msg)
