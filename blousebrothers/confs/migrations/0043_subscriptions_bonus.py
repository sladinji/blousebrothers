
from django.db import migrations
from decimal import Decimal


def create_tests(apps, schema_editor):
    """ Create test for conferencier to be able to test their own confs"""
    SubscriptionType = apps.get_model('confs', 'SubscriptionType')
    sub = SubscriptionType.objects.first()
    sub.bonus = Decimal('2')
    sub.save()



class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0042_auto_20170202_0955'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(create_tests),
    ]
