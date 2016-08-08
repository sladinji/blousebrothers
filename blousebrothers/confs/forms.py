from django import forms
from django.forms.models import inlineformset_factory, ModelForm
from djng.forms import NgModelForm, NgFormValidationMixin, NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _

from .models import(
        Conference,
        Question,
        Answer,
)

class ConferenceForm(NgModelFormMixin, NgModelForm, Bootstrap3FormMixin):
    class Meta:
        model = Conference
        exclude = ['owner']
        title = forms.CharField(label=_('Titre'), required=True, min_length=3, max_length=64)

AnswerFormSet = inlineformset_factory(
        Question,
        Answer,
        exclude=[ 'order'],
        extra = 5,
        max_num= 5,
        can_order=True, can_delete= True,
)
