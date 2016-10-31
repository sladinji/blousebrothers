from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import (
    Product,
    Category,
    )


class Command(BaseCommand):
    help = 'Delete all product in category "Nom de domaine"'

    def handle(self, *args, **options):
        Category.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(
                Product.objects.all().delete()
            )
        )

