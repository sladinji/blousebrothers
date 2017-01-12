from oscar.apps.catalogue.managers import BrowsableProductManager as BaseBrowsableProductManager
from cuser.middleware import CuserMiddleware


class BrowsableProductManager(BaseBrowsableProductManager):
    """
    Used to display browsable product in catalogue
    """

    def get_queryset(self):
        """
        Remove suscription
        """
        qs = super().get_queryset()
        user = CuserMiddleware.get_user()
        if not user or not user.is_staff :
            qs = qs.exclude(product_class__name='Abonnements')
        qs = qs.order_by('stockrecords__price_excl_tax')
        return qs
