from django.db import migrations


def fix_cards(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Deck = apps.get_model('cards', 'Deck')
    app = User.objects.get(username="apprendre")
    for card in app.created_cards.filter(anki_pkg__isnull=True):
        good_one = app.created_cards.filter(anki_pkg__isnull=False, content__contains=card.content.split("\n")[0]).first()
        if good_one:
            Deck.objects.filter(card_id=card.id).update(card_id=good_one.id)
        else:
            print("dead", Deck.objects.filter(card_id=card.id).count())
            Deck.objects.filter(card_id=card.id).all().delete()
        card.delete()
    app.created_cards.update(public=True)


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0006_auto_20170908_0951'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(fix_cards),
    ]
