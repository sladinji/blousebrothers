from django.db import migrations


def import_cards(apps, schema_editor):
    from blousebrothers.confs.management.commands.import_cards import Command
    Command().handle()


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(import_cards),
    ]
