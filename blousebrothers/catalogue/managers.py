from oscar.apps.catalogue.managers import BrowsableProductManager as BaseBrowsableProductManager
from cuser.middleware import CuserMiddleware


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
        qs = qs.prefetch_related('stockrecords')
        qs = qs.exclude(conf__deleted=True)
        qs = qs.exclude(conf__for_sale=False)
        user = CuserMiddleware.get_user()
        if not user or not user.is_staff:
            qs = qs.exclude(product_class__name='Abonnements')
        qs = qs.order_by('stockrecords__price_excl_tax')
        return qs
