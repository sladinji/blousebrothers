from oscar.apps.catalogue.managers import BrowsableProductManager as BaseBrowsableProductManager


class BrowsableProductManager(BaseBrowsableProductManager):
    """
    Used to display browsable product in catalogue
    """

    def get_queryset(self):
        """
        Remove suscription
        """
        qs = super().get_queryset()
        return qs.exclude(product_class__name='Abonnements')
