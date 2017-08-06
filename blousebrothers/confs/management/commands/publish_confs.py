from django.core.management.base import BaseCommand
from oscar.core.loading import get_classes
from blousebrothers.confs.models import Conference
from blousebrothers.confs.utils import get_or_create_product


ProductClass, Product, Category, ProductCategory, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'Category',
                         'ProductCategory', 'ProductImage'))


class Command(BaseCommand):
    help = 'Create products from confs'

    def handle(self, *args, **options):
        for conf in Conference.objects.filter(for_sale=True, edition_progress=100):
            if conf.products.count() > 0:
                self.stdout.write(
                    self.style.WARNING('{} "{}" already in shop ({}€)'.format(
                        conf.type, conf.title, conf.price)
                    )
                )
                continue
            get_or_create_product(conf)
            self.stdout.write(
                self.style.SUCCESS('{} "{}" created ({}€)'.format(
                    conf.type, conf.title, conf.price)
                )
            )
