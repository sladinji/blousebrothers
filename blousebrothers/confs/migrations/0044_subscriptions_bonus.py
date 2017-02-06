
from django.db import migrations
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from datetime import date


def fix_subscription(apps, schema_editor):
    Subscription = apps.get_model('confs', 'Subscription')
    SubscriptionType = apps.get_model('confs', 'SubscriptionType')

    # update presale sub past due date
    pdate = date.today() + relativedelta(months=+12)
    Subscription.objects.all().update(date_over=pdate)

    Subscription.objects.all().update(type_id=5)
    SubscriptionType.objects.exclude(id=5).delete()
    sub = SubscriptionType.objects.first()
    sub.bonus = Decimal('2')
    sub.save()

    # Update Abo product type

    Product = apps.get_model('catalogue', 'Product')
    ProductAttribute = apps.get_model('catalogue', 'ProductAttribute')
    ProductAttributeValue = apps.get_model('catalogue', 'ProductAttributeValue')

    abo = Product.objects.filter(title__icontains='abo').get()
    pclass = abo.product_class

    bonus = ProductAttribute(name='bonus', code='bonus', type='text')
    bonus.save()
    email_msg = ProductAttribute(name='email_msg', code='email_msg', type='richtext')
    email_msg.save()
    bonus_sponsor = ProductAttribute(name='bonus_sponsor', code='bonus_sponsor', type='text')
    bonus_sponsor.save()
    pclass.attributes.add(bonus, email_msg, bonus_sponsor)
    pclass.save()

    #add a 2€ bonus attribute to presale subscription
    mybonus = ProductAttributeValue(attribute=bonus, value_text='2.00', product=abo)
    mybonus.save()
    abo.attribute_values.add(mybonus)
    abo.save()


class Migration(migrations.Migration):

    dependencies = [
        ('confs', '0043_auto_20170206_0855'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(fix_subscription),
    ]
