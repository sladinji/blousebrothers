"""
This Oscar modules is overrided to define pricing strategy.
"""
from decimal import Decimal as D

from oscar.apps.partner import strategy, prices, availability

DEFAULT_RATE = D('0.0')

PRODUCT_CLASSES_RATES = {
    'cours': 0,
    'medias': D('0.055'),
}


class Selector(object):
    """
    Custom selector to return a FR-specific strategy that charges VAT
    """

    def strategy(self, request=None, user=None, **kwargs):
        return FRStrategy(request)


class FrenchFixedRateTax(object):
    """
    This mixin applies a french fixed rate tax to the base price from the product's
    stockrecord. How is the rate discovered:
    _ found in PRODUCT_CLASSES_RATES setting
    _ otherwise apply default rate
    """
    def pricing_policy(self, product, stockrecord):
        self.rate = PRODUCT_CLASSES_RATES.get(
            product.get_product_class().slug,
            DEFAULT_RATE)
        if product.conf:
            return prices.FixedPrice(
                currency='EUR',
                excl_tax=product.conf.price)
        if not stockrecord:
            return prices.Unavailable()
        return prices.FixedPrice(
            currency=stockrecord.price_currency,
            excl_tax=stockrecord.price_excl_tax,
            tax=stockrecord.price_excl_tax * self.rate)


class FRStrategy(
        strategy.UseFirstStockRecord,
        FrenchFixedRateTax,
        strategy.StockRequired,
        strategy.Structured):
    """
    Typical FR strategy for physical goods.
    - There's only one warehouse/partner so we use the first and only stockrecord
    - Enforce stock level.  Don't allow purchases when we don't have stock.
    - Charge FR VAT on prices.  Assume everything is standard-rated.
    """
    def availability_policy(self, product, stockrecord):
        if product.conf and product.conf.for_sale and product.conf.owner.gave_all_mangopay_info():
            return availability.Available()
        return availability.Unavailable()

