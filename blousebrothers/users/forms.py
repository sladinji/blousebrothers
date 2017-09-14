from decimal import Decimal
from django import forms
from django.utils.translation import ugettext_lazy as _
from oscar.forms.widgets import DatePickerInput
from localflavor.generic.forms import IBANFormField, BICFormField, DateField
from django.utils.safestring import mark_safe
from blousebrothers.confs.models import Speciality


from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name',
                  'birth_date', 'country_of_residence', 'nationality', 'email',
                  'university', 'degree',
                  'address1', 'address2', 'zip_code',
                  'city', 'speciality', 'bio', 'mobile',
                  ]
    birth_date = forms.DateField(widget=DatePickerInput, label=_("Date de naissance"))


class UserSmallerForm(UserForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'address1', 'address2', 'zip_code', 'city', 'country_of_residence',
                  'nationality', 'birth_date', ]


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


class PayOutForm(forms.Form):
    debited_funds = forms.DecimalField(label=_('Montant en euros'))

    def __init__(self, **kwargs):
        max_value = kwargs.pop('max_value')
        super().__init__(**kwargs)
        self.fields['debited_funds'].max_value = Decimal(max_value)
        self.fields['debited_funds'].help_text = "Maximum {} €".format(max_value)


class IbanForm(forms.Form):
    iban = IBANFormField(label=_("IBAN"), required=True)
    bic = BICFormField(label=_("BIC"), required=True)


class EmailInvitationForm(forms.Form):
    email = forms.EmailField(label=_('Email de ton filleul'), required=True)


class ImageForm(forms.Form):
    image = forms.ImageField(
        label=mark_safe("<i class='fa fa-camera'></i> Prend une photo de carte d'étudiant"),
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'btn btn-upload'}))


class CardRegistrationForm(forms.Form):
    cardRegistrationURL = forms.CharField(widget=forms.HiddenInput())
    accessKeyRef = forms.CharField(widget=forms.HiddenInput())
    returnURL = forms.CharField(widget=forms.HiddenInput())
    data = forms.CharField(widget=forms.HiddenInput())
    cardNumber = forms.CharField(label=_('Numéro de la carte'), required=True,
                                 widget=forms.TextInput(
                                     attrs={'data-inputmask': "'mask': '9999999999999999'"}
                                 ))
    cardExpirationDate = DateField(label=_("Date d'expiration"), required=True,
                                   help_text="ex. : 1219",
                                   widget=forms.TextInput(
                                       attrs={'data-inputmask': "'mask': '9999'"}
                                   )
                                   )
    cardCvx = forms.CharField(label=_("Code de vérification"), required=True,
                              help_text="code à 3 chiffres au dos de la carte",
                              widget=forms.TextInput(
                                  attrs={'data-inputmask': "'mask': '999'"}
                              )
                              )


class DemoForm(forms.Form):
    specialities = forms.ChoiceField(
        choices=[(spe.id, spe.name) for spe in Speciality.objects.filter(
            conferences__for_sale=True, conferences__price=0
        ).distinct().all()
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=mark_safe("&nbsp;&nbsp;&nbsp;Je veux travailler :")
    )
