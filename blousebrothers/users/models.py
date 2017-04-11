# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.core.mail import mail_admins
from django_countries.fields import CountryField
from django.db.models.signals import post_init, pre_save

from djmoney.models.fields import MoneyField
from allauth.account.signals import user_signed_up
from shortuuidfield import ShortUUIDField
from invitations.models import Invitation

from mangopay.models import (
    MangoPayNaturalUser,
    MangoPayWallet,
    MangoPayTransfer,
    MangoPayBankAccount,
    MangoPayPayOut,
)
from blousebrothers.catalogue.models import Product
from blousebrothers.confs.models import Conference

logger = logging.getLogger(__name__)

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
    address1 = models.CharField(_("Adresse 1"), blank=False, null=True, max_length=50)
    """Address first line"""
    address2 = models.CharField(_("Adresse 2"), blank=True, max_length=50)
    """Address second line"""
    city = models.CharField(_("Ville"), blank=False, null=True, max_length=50)
    """City"""
    zip_code = models.CharField(_("Code postal"), blank=False, null=True, max_length=20)
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
    status = models.CharField(_("Status"), max_length=20, default="registred", null=True)
    status_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    previous_status = None  # place holder to check status change

    @property
    def gave_all_required_info(self):
        """Used for permission management"""
        if self.wanabe_conferencier or self.is_conferencier:
            return self.university and self.first_name and self.last_name and self.degree
        return True

    @property
    def gave_all_mangopay_info(self):
        return bool(self.birth_date and self.country_of_residence and self.nationality and
                    self.first_name and self.last_name and self.address1 and self.city and
                    self.zip_code)

    @property
    def mangopay_user(self):
        if self.gave_all_mangopay_info:
            mp_user, mpu_created = MangoPayNaturalUser.objects.get_or_create(user=self)
            if mpu_created:
                mp_user.birthday = self.birth_date
                mp_user.country_of_residence = self.country_of_residence
                mp_user.nationality = self.nationality
                mp_user.create()
            return mp_user

    def remove_inactive_cards(self):
        for cr in self.mangopay_user.mangopay_card_registrations.all():
            cr.mangopay_card.request_card_info()
            if not cr.mangopay_card.is_active:
                cr.mangopay_card.delete()

    @property
    def has_more_than_one_card(self):
        return len([x for x in self.mangopay_user.mangopay_card_registrations.all()
                    if x.mangopay_card.mangopay_id]) > 1

    @property
    def has_at_least_one_card(self):
        return len([x for x in self.mangopay_user.mangopay_card_registrations.all()
                    if x.mangopay_card.mangopay_id]) > 0

    def _get_or_create_wallet(self, description):
        wallet, w_created = MangoPayWallet.objects.get_or_create(
            mangopay_user=self.mangopay_user,
            description=description
        )
        # Sychronize with MangoPay
        if w_created or not wallet.mangopay_id:
            wallet.mangopay_user = self.mangopay_user
            wallet.create(description=description)
        return wallet

    @property
    def wallet(self):
        return self._get_or_create_wallet("{}'s personal wallet".format(self.username))

    @property
    def wallet_bonus(self):
        return self._get_or_create_wallet("{}'s bonus wallet".format(self.username))

    @property
    def bank_account(self):
        return MangoPayBankAccount.objects.filter(mangopay_user=self.mangopay_user).first()

    @property
    def subscription(self):
        subs = [x for x in self.subs.all().order_by('-date_created') if not x.is_past_due]
        if subs:
            return subs[0]

    @property
    def products(self):
        return Product.objects.filter(conf__owner=self)

    def give_bonus(self, amount):
        bb = User.objects.get(username="BlouseBrothers")
        transfer = MangoPayTransfer()
        transfer.mangopay_credited_wallet = self.wallet_bonus
        transfer.mangopay_debited_wallet = bb.wallet_bonus
        transfer.debited_funds = amount
        transfer.save()
        transfer.create()
        if transfer.status == 'SUCCEEDED':
            return True

    def handle_subscription_bonus(self, subscription=None):
        if not subscription:
            subscription = self.subscription

        if subscription and not subscription.bonus_taken and self.gave_all_mangopay_info:
            if self.give_bonus(subscription.type.bonus):
                subscription.bonus_taken = True
                subscription.save()
                return subscription.type.bonus

    def handle_sponsor_bonus(self, subscription=None):
        if not subscription:
            subscription = self.subscription
        if not subscription or subscription.bonus_sponsor_taken:
            return
        invitation = Invitation.objects.filter(email=self.email, accepted=True).first()
        if invitation:
            if invitation.inviter.give_bonus(subscription.type.bonus_sponsor):
                subscription.bonus_sponsor_taken = True
                subscription.save()
                return invitation

    @property
    def mango_address(self):
        return {
            "AddressLine1": self.address1,
            "AddressLine2": self.address2,
            "City": self.city,
            "Region": "",
            "PostalCode": self.zip_code,
            "Country": self.country_of_residence.code,
        }

    def create_bank_account(self, iban, bic):
        """
        Create user's bank account.
        """
        bank_account = MangoPayBankAccount()
        bank_account.mangopay_user = self.mangopay_user
        bank_account.iban = iban
        bank_account.bic = bic
        bank_account.address = self.mango_address
        bank_account.create()

    def payout(self, debited_funds):
        """
        Transfer money from user's wallet to his bank account.
        """
        payout = MangoPayPayOut()
        payout.mangopay_user = self.mangopay_user
        payout.mangopay_wallet = self.wallet
        payout.mangopay_bank_account = self.bank_account
        payout.debited_funds = debited_funds
        payout.fees = 0
        payout.save()
        payout.create()
        return payout


class Sale(models.Model):
    conferencier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    conf = models.ForeignKey(Conference, on_delete=models.SET_NULL, related_name='sales', null=True)
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="purchases")
    transfer = models.ForeignKey(MangoPayTransfer, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='sales')
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


##################################################################################
#                  _________.__                     .__                          #
#                 /   _____/|__| ____   ____ _____  |  |   ______                #
#                 \_____  \ |  |/ ___\ /    \\__  \ |  |  /  ___/                #
#                 /        \|  / /_/  >   |  \/ __ \|  |__\___ \                 #
#                /_______  /|__\___  /|___|  (____  /____/____  >                #
#                        \/   /_____/      \/     \/          \/                 #
#                                                                       __       #
#      _____ _____    ____ _____     ____   ____   _____   ____   _____/  |_     #
#     /     \\__  \  /    \\__  \   / ___\_/ __ \ /     \_/ __ \ /    \   __\    #
#    |  Y Y  \/ __ \|   |  \/ __ \_/ /_/  >  ___/|  Y Y  \  ___/|   |  \  |      #
#    |__|_|  (____  /___|  (____  /\___  / \___  >__|_|  /\___  >___|  /__|      #
#          \/     \/     \/     \//_____/      \/      \/     \/     \/          #
#                                                                                #
##################################################################################


email_template = '''
Nom : {}
Email : {}
Lien : {}{}{}'''


@receiver(user_signed_up, dispatch_uid="notify_signup")
def notify_signup(request, user, **kwargs):
    """
    send a mail to admin
    """
    try:
        msg = email_template.format(user.name,
                                    user.email,
                                    'https://' if request.is_secure() else 'http://',
                                    request.get_host(),
                                    reverse('dashboard:user-detail',
                                            args=(user.id,)
                                            )
                                    )
        mail_admins('Nouvelle inscription', msg)
    except:
        logger.exception("Error sending email info for new inscription")


@receiver(pre_save, sender=User)
def update_status_timestamp(sender, **kwargs):
    """
    Method to update status_timestamp if status has changed.
    """
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    if instance.previous_status != instance.status or created:
        instance.status_timestamp = datetime.now()


@receiver(post_init, sender=User)
def remember_status(sender, **kwargs):
    """
    Method to set previous_status after init.
    """
    instance = kwargs.get('instance')
    instance.previous_status = instance.status
