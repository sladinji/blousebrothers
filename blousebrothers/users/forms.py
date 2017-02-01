from decimal import Decimal
from django import forms
from django.utils.translation import ugettext_lazy as _
from oscar.forms.widgets import DatePickerInput

from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'birth_date', 'country_of_residence', 'nationality', 'email',
                  'university', 'degree',
                  'address1', 'address2', 'zip_code',
                  'city', 'speciality', 'bio', 'mobile',
                  ]
    birth_date = forms.DateField(widget=DatePickerInput, label=_("Date de naissance"))


class WalletForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
                'birth_date', 'country_of_residence', 'nationality',
                ]


class PayInForm(forms.Form):
    credit = forms.DecimalField(label=_('Montant en euros'),
                                max_value=Decimal('250.0'),
                                min_value=Decimal('5.00'),
                                help_text=_('Minimum 5€'),
                                )

class EmailInvitationForm(forms.Form):
    email = forms.EmailField(label=_('Email de ton filleul'))

class CardRegistrationForm(forms.Form):
    cardRegistrationURL = forms.CharField(widget=forms.HiddenInput())
    accessKeyRef = forms.CharField(widget=forms.HiddenInput())
    returnURL = forms.CharField(widget=forms.HiddenInput())
    data = forms.CharField(widget=forms.HiddenInput())
    cardNumber = forms.CharField(label=_('Numéro de la carte'), required=True)
    cardExpirationDate = forms.CharField(label=_("Date d'expiration"), required=True,
                                         help_text="ex. : 1219")
    cardCvx = forms.CharField(label=_("Code de vérification"), required=True,
                                         help_text="code à 3 chiffres au dos de la carte")
