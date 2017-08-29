from django.apps import apps
from blousebrothers.users.forms import EmailInvitationForm

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')
invit_form = EmailInvitationForm()


def subscriptions(request):
    pclass, __ = ProductClass.objects.get_or_create(
        name="Abonnements",
        requires_shipping=False,
        track_stock=False,
    )
    subs = Product.objects.filter(product_class=pclass).order_by('id')
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
