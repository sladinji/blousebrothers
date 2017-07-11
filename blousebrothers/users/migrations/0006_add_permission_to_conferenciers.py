from django.db import migrations


def add_permission(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Permission = apps.get_model('auth', 'Permission')
    try:
        perm = Permission.objects.get(name='Can add conference')
        for user in User.objects.filter(is_conferencier=True).exclude(user_permissions=perm):
            user.user_permissions.add(perm)
            user.save()
    except:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20161120_0940'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(add_permission),
    ]
