from django.apps import apps
from django.utils.safestring import mark_safe
from mangopay.models import (
    MangoPayNaturalUser,
    MangoPayWallet,
)

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')


def subscriptions(request):
    pclass, __ = ProductClass.objects.get_or_create(
        name="Abonnements",
        requires_shipping=False,
        track_stock=False,
    )
    subs = Product.objects.filter(product_class=pclass)
    return {'subscriptions': subs}


def dday(request):
    from datetime import datetime
    d = datetime(2017, 2, 14) - datetime.now()
    return {'dday': d.days}


def balance(request):
    try:
        return {'balance': request.user.wallet.balance() + request.user.wallet_bonus.balance()}
    except:
        return {'balance': mark_safe('<span style="color:orange;">Activer porte-monnaie</span>')}
