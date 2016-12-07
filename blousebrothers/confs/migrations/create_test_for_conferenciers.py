from django.db import migrations


def create_tests(apps, schema_editor):
    """ Create test for conferencier to be able to test their own confs"""
    Test = apps.get_model('confs', 'Test')
    Conference = apps.get_model('confs', 'Conference')
    for conf in Conference.objects.filter(edition_progress=100):
        Test.objects.get_or_create(conf=conf, student=conf.owner)


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0025_auto_20161206_0924'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(create_tests),
    ]
