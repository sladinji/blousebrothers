from django import forms
from django.forms.models import inlineformset_factory, ModelForm, modelformset_factory
from djng.forms import NgModelForm, NgFormValidationMixin, NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _
from multiupload.fields import MultiFileField, MultiFileInput
from django_select2.forms import ModelSelect2MultipleWidget
from django.utils.safestring import mark_safe

from .models import(
    Conference,
    Question,
    Answer,
    Item,
    Speciality,
)

class EndingConferenceForm(ModelForm, Bootstrap3FormMixin):
    items = forms.ModelMultipleChoiceField(
                widget=ModelSelect2MultipleWidget(
                                queryset=Item.objects.order_by('number').all(),
                                search_fields=['name__icontains']
                            ),
        queryset=Item.objects.all(),
        required=True,
        help_text=mark_safe(_('Ne sélectionnez que les items abordés de manière '
                    '<strong>significative</strong> dans votre dossier'))
            )
    specialities = forms.ModelMultipleChoiceField(
                widget=ModelSelect2MultipleWidget(
                                queryset=Speciality.objects.order_by('name').all(),
                                search_fields=['name__icontains']
                            ),
        queryset=Speciality.objects.all(),
        required=True,
        label=_("Matières abordées"),
    )



class ConferenceForm(ModelForm,  Bootstrap3FormMixin):

    form_name = 'conf_form'
    field_order = ['title', 'type', 'summary']
    class Meta:
        model = Conference
        exclude = ['owner', 'edition_progress', 'items', 'specialities', 'images', 'statement']
