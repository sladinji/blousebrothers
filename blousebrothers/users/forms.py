from django import forms
from django.utils.translation import ugettext_lazy as _
from oscar.forms.widgets import DatePickerInput

from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'address1', 'address2', 'zip_code',
                'city', 'email', 'university', 'degree', 'mobile',
                ]


class WalletForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['birth_date', 'country_of_residence', 'nationality']
    birth_date = forms.DateField(widget=DatePickerInput, label=_("Date de naissance"))
