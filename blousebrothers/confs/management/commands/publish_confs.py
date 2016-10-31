from decimal import Decimal as D
from django.core.management.base import BaseCommand
from oscar.core.loading import get_class, get_classes
from oscar.apps.partner.models import Partner, StockRecord
from blousebrothers.confs.models import Conference


ProductClass, Product, Category, ProductCategory, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'Category',
                         'ProductCategory', 'ProductImage'))
class Command(BaseCommand):
    help = 'Create products from confs'

    def load_conf(self, conf):
        try:
            # Category names should be unique at the depth=1
            cat = Category.objects.get(depth=1, name=conf.type)
        except Category.DoesNotExist:
            cat = Category.add_root(name=conf.type)

        # Get or create product class
        prod_class , created = ProductClass.objects.get_or_create(name=conf.type,
                                                                    requires_shipping=False,
                                                                    track_stock=False)
        # Now we got all we need to create product
        prod, _ = Product.objects.get_or_create(structure=Product.STANDALONE,
                                               title=conf.title,
                                               product_class=prod_class,
                                               )
        prod.description = conf.summary
        if conf.statement :
            prod.description += '\n' + conf.statement[:200] + "..."
        #prod.images.add(ProductImagei(
        prod.conf = conf
        prod.save()

        ProductCategory.objects.get_or_create(product=prod, category=cat)
        partner, _ = Partner.objects.get_or_create(name="NOUS")
        stock, _ = StockRecord.objects.get_or_create(product=prod, partner=partner)
        stock.partner_sku = (conf.slug)
        stock.partner = partner
        stock.product = prod
        stock.price_excl_tax = D(conf.price)
        stock.save()
        self.stdout.write(
            self.style.SUCCESS('{} "{}" created ({}€)'.format(
                conf.type, conf.title, conf.price)
            )
        )

    def handle(self, *args, **options):
        for conf in Conference.objects.filter(edition_progress=100):
                self.load_conf(conf)
