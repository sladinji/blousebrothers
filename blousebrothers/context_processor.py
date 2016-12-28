from django.apps import apps
from mangopay.models import (
    MangoPayNaturalUser,
    MangoPayWallet,
)

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')


def subscriptions(request):
        subs = Product.objects.filter(product_class=ProductClass.objects.get(name="Abonnements"))
        return {'subscriptions': subs}


def balance(request):
    try:
        mangopay_user = MangoPayNaturalUser.objects.get(user=request.user)
        wallet = MangoPayWallet.objects.get(mangopay_user=mangopay_user)
        return {'balance': wallet.balance()}
    except:
        return {'balance': 'EUR 0.00'}
