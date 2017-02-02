from django import forms
from django.forms.models import ModelForm
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget
from django.utils.safestring import mark_safe

from .models import(
    Conference,
    Item,
    Speciality,
    Test,
)


class ConferenceFinalForm(ModelForm, Bootstrap3FormMixin):

    class Meta:
        model = Conference
        fields = ['items', 'specialities', 'price', 'for_sale']

    items = forms.ModelMultipleChoiceField(
        widget=ModelSelect2MultipleWidget(
            queryset=Item.objects.order_by('number').all(),
            search_fields=['name__icontains']
        ),
        queryset=Item.objects.all(),
        required=True,
        help_text=mark_safe(_('Ne sélectionner que les items abordés de manière '
                    '<strong>significative</strong> dans le dossier'))
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.type == 'LCA':
            self.fields.pop('items')
            self.fields.pop('specialities')


class ConferenceForm(ModelForm,  Bootstrap3FormMixin):

    class Meta:
        model = Conference
        fields = ['title', 'type', 'summary']

    form_name = 'conf_form'


class RefundForm(ModelForm, Bootstrap3FormMixin):
    class Meta:
        model = Test
        fields = []
    msg = forms.CharField(label=_('Message'), widget=forms.Textarea)

