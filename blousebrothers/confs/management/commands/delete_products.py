from django.core.management.base import BaseCommand
from oscar.core.loading import get_class, get_classes

Product, Category = get_classes('catalogue.models', ('Product', 'Category'))


class Command(BaseCommand):
    help = 'Delete all product in category "Nom de domaine"'

    def handle(self, *args, **options):
        Category.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(
                Product.objects.all().delete()
            )
        )

