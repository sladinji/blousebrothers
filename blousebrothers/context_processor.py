from django.apps import apps
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
    d = datetime(2017, 1, 23) - datetime.now()
    return {'dday': d.days}


def balance(request):
    try:
        mangopay_user = MangoPayNaturalUser.objects.get(user=request.user)
        wallet = MangoPayWallet.objects.get(mangopay_user=mangopay_user)
        return {'balance': wallet.balance()}
    except:
        return {'balance': 'EUR 0.00'}
