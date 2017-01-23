from django.core.management.base import BaseCommand
from oscar.core.loading import get_classes
from blousebrothers.confs.models import Conference
from blousebrothers.confs.utils import create_product


ProductClass, Product, Category, ProductCategory, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'Category',
                         'ProductCategory', 'ProductImage'))


class Command(BaseCommand):
    help = 'Create products from a given conf slug'

    def add_arguments(self, parser):
        parser.add_argument('slug', type=str)

    def handle(self, *args, **options):
        conf = Conference.objects.get(slug=options['slug'])
        create_product(conf)
        self.stdout.write(
            self.style.SUCCESS('{} "{}" created ({}€)'.format(
                conf.type, conf.title, conf.price)
            )
        )
