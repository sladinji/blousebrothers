from django import forms
from django.forms.models import ModelForm
from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2TagWidget
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
        fields = ['question', 'content', 'image']

    question = forms.CharField()
    image = forms.ImageField(
        label=mark_safe("<i class='fa fa-camera'></i> Ajouter une image"),
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'btn btn-upload'}))


class TagSelect2TagWidget(ModelSelect2TagWidget):
    """
    Widget allowing tag creation if missing.
    """
    queryset = Tag.objects.order_by('name').all()
    search_fields = ['name__icontains']

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        return [Tag.objects.get_or_create(name=value)[0].pk for value in values]


class FinalizeCardForm(ModelForm, Bootstrap3FormMixin):

    class Meta:
        model = Card
        fields = ['tags', 'specialities', 'items']

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
        widget=TagSelect2TagWidget(),
        queryset=Tag.objects.all(),
        required=False,
        label=_("Tags (séparés par des espaces)"),
        help_text=mark_safe(_('Mets des tags qui te permettront de regrouper tes fiches par thèmes '
                              '(par exemple: "zona" "mnémotechnique" "difficile" "icono")'))
    )


class AnkiFileForm(forms.Form):
    ankifile = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(),
    )
