from django.conf import settings
from django.apps import apps

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')

def subscriptions(request):
        subs = Product.objects.filter(product_class=ProductClass.objects.get(name="Abonnements"))
        return {'subscriptions': subs}
