from django.apps import apps
from django.utils.safestring import mark_safe
from blousebrothers.users.forms import EmailInvitationForm

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')


def subscriptions(request):
    pclass, __ = ProductClass.objects.get_or_create(
        name="Abonnements",
        requires_shipping=False,
        track_stock=False,
    )
    subs = Product.objects.filter(product_class=pclass).exclude(id=46)
    return {'subscriptions': subs}


def balance(request):
    try:
        return {'balance': request.user.wallet.balance() + request.user.wallet_bonus.balance()}
    except:
        return {'balance': mark_safe('<span style="color:orange;">Activer mon compte</span>')}


def invit_form(request):
    return {'invit_form': EmailInvitationForm()}
