from django import forms
from django.forms.models import ModelForm
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget
from django.utils.safestring import mark_safe

from blousebrothers.confs.models import Item, Speciality
from .models import Card, Tag


class UpdateCardForm(ModelForm, Bootstrap3FormMixin):
    class Meta:
        model = Card
        fields = ['content', ]


class CreateCardForm(ModelForm, Bootstrap3FormMixin):
    class Meta:
        model = Card
        fields = ['question', 'content']

    question = forms.CharField()


class FinalizeCardForm(ModelForm, Bootstrap3FormMixin):

    class Meta:
        model = Card
        fields = ['specialities', 'items', 'tags']

    items = forms.ModelMultipleChoiceField(
        widget=ModelSelect2MultipleWidget(
            queryset=Item.objects.order_by('number').all(),
            search_fields=['name__icontains']
        ),
        queryset=Item.objects.all(),
        required=False,
        help_text=mark_safe(_('Ne sélectionner que les items abordés de manière '
                              '<strong>significative</strong> dans le dossier'))
    )
    specialities = forms.ModelMultipleChoiceField(
        widget=ModelSelect2MultipleWidget(
            queryset=Speciality.objects.order_by('name').all(),
            search_fields=['name__icontains']
        ),
        queryset=Speciality.objects.all(),
        required=False,
        label=_("Matières abordées"),
    )
    tags = forms.ModelMultipleChoiceField(
        widget=ModelSelect2MultipleWidget(
            queryset=Tag.objects.order_by('name').all(),
            search_fields=['name__icontains']
        ),
        queryset=Tag.objects.all(),
        required=False,
        label=_("Tags"),
    )


class AnkiFileForm(forms.Form):
    ankifile = forms.FileField(
        label=mark_safe("<i class='fa fa-file'></i> Choisis ton fichier Anki"),
        required=True,
        widget=forms.ClearableFileInput(),
    )
