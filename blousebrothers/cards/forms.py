from django import forms
from django.forms.models import ModelForm
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget
from django.utils.safestring import mark_safe

from blousebrothers.confs.models import Item, Speciality
from .models import Card


class CreateCardForm(ModelForm, Bootstrap3FormMixin):

    class Meta:
        model = Card
        fields = ['specialities', 'items', 'title_tmp', 'section_tmp', 'content']

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
