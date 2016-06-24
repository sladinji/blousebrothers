from django import forms
from oscar.apps.dashboard.catalogue.forms import ProductClassSelectForm as OriginalProductClassSelectForm
from oscar.apps.dashboard.catalogue.forms import ProductClass
from django.utils.translation import ugettext_lazy as _


class ProductClassSelectForm(OriginalProductClassSelectForm):
    product_class = forms.ModelChoiceField(
        label=_("Créer un nouveau sujet de type"),
        empty_label=_("-- Choose type --"),
        queryset=ProductClass.objects.all())
