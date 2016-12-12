from django.core.management.base import BaseCommand
from blousebrothers.confs.models import Conference

class Command(BaseCommand):
    help = 'Check conference images given his conference slug'
    def add_arguments(self, parser):
        # This is an optional argument
        parser.add_argument('slug', nargs='+', type=str)

    def handle(self, *args, **options):
        print(options["slug"])
        obj = Conference.objects.prefetch_related(
            "questions__answers",
            "questions__images",
        ).get(slug=options['slug'][0])
        obj.check_images()
