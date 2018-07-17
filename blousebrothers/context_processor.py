from django.apps import apps
from django import forms

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')

class EmailInvitationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email de ton collègue'}), label="",
                             required=True)


invit_form = EmailInvitationForm()


def subscriptions(request):
    pclass, __ = ProductClass.objects.get_or_create(
        name="Abonnements",
        requires_shipping=False,
        track_stock=False,
    )
    subs = Product.objects.filter(
        product_class=pclass
    ).exclude(
        categories__name="__HIDDEN"
    ).order_by('id')
    return {'subscriptions': subs}


def invit_form(request):
    """
    Invit form is included in man views. It can be updated (required field missing...) so
    we use global var and reset it before return.
    """
    global invit_form
    ret = {'invit_form': invit_form}
    invit_form = EmailInvitationForm()
    return ret
