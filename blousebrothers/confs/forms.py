from django import forms
from django.forms.models import inlineformset_factory, ModelForm, modelformset_factory
from djng.forms import NgModelForm, NgFormValidationMixin, NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _
from multiupload.fields import MultiFileField, MultiFileInput

from .models import(
        Conference,
        Question,
        Answer,
)

class ConferenceForm(NgModelFormMixin, NgFormValidationMixin, NgModelForm,  Bootstrap3FormMixin):

    scope_prefix = 'conf_data'
    form_name = 'conf_form'
    field_order = ['title', 'type', 'images', 'summary', 'statement', 'items', 'specialities']
    class Meta:
        model = Conference
        exclude = ['owner', 'edition_progress']
    images = MultiFileField(min_num=0, max_num=3,required=False, max_file_size=1024*1024*5,
                             widget=MultiFileInput(attrs={'class':'no-border-form'}),
                            label=_("Images de l'énoncé"),
                            help_text=_("Vous pouvez selectionner pulsieurs images"),
                            )


    field_css_classes = {
            '*': 'form-group has-feedback',
            'images': "ng-class:{'ng-hide':conf_data['type']==='QI'}",
    }
