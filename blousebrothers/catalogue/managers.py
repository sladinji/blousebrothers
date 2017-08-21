from django.db.models import Prefetch
from oscar.apps.catalogue.managers import BrowsableProductManager as BaseBrowsableProductManager
from cuser.middleware import CuserMiddleware
from blousebrothers.confs.models import Test


class BrowsableProductManager(BaseBrowsableProductManager):
    """
    Used to display browsable product in catalogue
    """

    def get_queryset(self):
        """
        Remove suscription and deleted confs
        """
        qs = super().get_queryset()
        qs = qs.prefetch_related('conf__owner')
        qs = qs.prefetch_related('conf__specialities')
        qs = qs.prefetch_related('stockrecords')
        qs = qs.exclude(conf__deleted=True)
        qs = qs.exclude(conf__for_sale=False)
        user = CuserMiddleware.get_user()
        if user and user.is_authenticated():
            qs = qs.prefetch_related(
                Prefetch(
                    'conf__tests',
                    queryset=Test.objects.filter(student=user, finished=True),
                    to_attr="done_tests",
                )
            )
        if not user or not user.is_staff:
            qs = qs.exclude(product_class__name='Abonnements')
        qs = qs.order_by('stockrecords__price_excl_tax')
        return qs
