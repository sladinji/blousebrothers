from django.db  import models

from oscar.apps.catalogue.abstract_models import AbstractProduct

class Product(AbstractProduct):
    conf = models.ForeignKey('confs.Conference', related_name='products', default=None,
                             null=True)
    for_sale = models.BooleanField(default=False)


from oscar.apps.catalogue.models import *  # noqa
