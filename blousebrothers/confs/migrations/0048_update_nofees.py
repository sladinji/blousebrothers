from django.db import migrations
from datetime import datetime


def update_nofees(apps, schema_editor):
    Conference = apps.get_model('confs', 'Conference')
    Conference.objects.filter(
        edition_progress=100,
        date_created__lt=datetime(2016, 12, 31),
    ).update(
        no_fees=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0047_auto_20170208_1029'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(update_nofees),
    ]
