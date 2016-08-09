from django import forms
from django.forms.models import inlineformset_factory, ModelForm, modelformset_factory
from djng.forms import NgModelForm, NgFormValidationMixin, NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _

from .models import(
        Conference,
        Question,
        Answer,
)

class ConferenceForm(NgModelFormMixin, NgFormValidationMixin, NgModelForm,  Bootstrap3FormMixin):
    scope_prefix = 'conf_data'
    form_name = 'conf_form'
    class Meta:
        model = Conference
        exclude = ['owner']
        title = forms.CharField(label=_('Titre'), required=True, min_length=3, max_length=64)

class QuestionForm(NgModelFormMixin, NgFormValidationMixin, NgModelForm,  Bootstrap3FormMixin):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerForm(ModelForm, Bootstrap3FormMixin):
    class Meta:
        model = Answer
        fields = ('question', 'answer', 'explaination', 'correct')

AnswerFormSet = modelformset_factory(
        Answer,
        exclude=[ 'order'],
        extra = 5,
        max_num= 5,
        can_order=True, can_delete= True,
        form=AnswerForm,
)

    #widgets={'name': Textarea(attrs={'cols': 80, 'rows': 20})})

