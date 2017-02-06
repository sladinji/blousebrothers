
from django.db import migrations
from decimal import Decimal


def fix_subscription(apps, schema_editor):
    """ Create test for conferencier to be able to test their own confs"""
    Subscription = apps.get_model('confs', 'Subscription')
    SubscriptionType = apps.get_model('confs', 'SubscriptionType')
    Subscription.objects.all().update(type_id=5)
    SubscriptionType.objects.exclude(id=5).delete()
    sub = SubscriptionType.objects.first()
    sub.bonus = Decimal('2')
    sub.save()

    # Update Abo product type
    Product = apps.get_model('catalogue', 'Product')
    ProductAttribute = apps.get_model('catalogue', 'ProductAttribute')
    abo = Product.objects.filter(title__icontains='abo').get()
    pclass = abo.product_class
    bonus = ProductAttribute(name='bonus', code='bonus', type='text')
    bonus.save()
    email_msg = ProductAttribute(name='email_msg', code='email_msg', type='richtext')
    email_msg.save()
    pclass.attributes.add(bonus, email_msg)
    pclass.save()



class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0043_auto_20170206_0855'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(fix_subscription),
    ]
