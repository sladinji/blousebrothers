import re
from django.db import migrations


def add_permission(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        user.status = re.sub('_+', '_', user.status)
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20170628_0946'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(add_permission),
    ]
