from django.db import migrations


def private_ophtalmo(apps, schema_editor):
    Speciality = apps.get_model('confs', 'Speciality')
    Card = apps.get_model('cards', 'Card')
    User = apps.get_model('users', 'User')
    bb = User.objects.get(username="BlouseBrothers")
    ophta = Speciality.objects.get(name="Ophtalmologie")
    Card.objects.filter(public=True, specialities__in=[ophta]).exclude(author=bb).update(public=False)


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0008_deck_trashed'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(private_ophtalmo),
    ]
