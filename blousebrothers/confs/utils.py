from decimal import Decimal as D
from oscar.core.loading import get_classes
from oscar.apps.partner.models import Partner, StockRecord


ProductClass, Product, Category, ProductCategory, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'Category',
                         'ProductCategory', 'ProductImage'))


def load_conf(conf):
    try:
        # Category names should be unique at the depth=1
        cat = Category.objects.get(depth=1, name=conf.type)
    except Category.DoesNotExist:
        cat = Category.add_root(name=conf.type)

    # Get or create product class
    prod_class, created = ProductClass.objects.get_or_create(name=conf.type,
                                                             requires_shipping=False,
                                                             track_stock=False)
    # Now we got all we need to create product
    prod, _ = Product.objects.get_or_create(structure=Product.STANDALONE,
                                            title=conf.title,
                                            product_class=prod_class,
                                            )
    prod.description = conf.summary
    if conf.statement:
        prod.description += '\n' + conf.statement[:200] + "..."
        #if conf.images.first():
        #    im = ProductImage(product=prod, display_order=1)
        #    cim = conf.images.first()
        #    im.original = cim.image
        #    im.save()
        #    prod.conf = conf
        #    prod.save()

    ProductCategory.objects.get_or_create(product=prod, category=cat)
    partner, _ = Partner.objects.get_or_create(name="NOUS")
    stock, _ = StockRecord.objects.get_or_create(product=prod, partner=partner)
    stock.partner_sku = (conf.slug)
    stock.partner = partner
    stock.product = prod
    stock.price_excl_tax = D(conf.price)
    stock.save()
