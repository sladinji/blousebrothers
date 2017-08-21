from django.db import migrations


def update_stats(apps, schema_editor):
    from blousebrothers.confs.management.commands.update_stats import Command
    Command().handle()


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0050_auto_20170821_0838'),
        ('users', '0017_set_score'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(update_stats),
    ]
