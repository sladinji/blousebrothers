from django.conf import settings
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from django.utils import timezone

import stripe
from django.apps import apps
import logging


logger = logging.getLogger(__name__)
Source = apps.get_model('payment', 'Source')
Order = apps.get_model('order', 'Order')


class Facade(object):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    @staticmethod
    def get_friendly_decline_message(error):
        return 'The transaction was declined by your bank - please check your bankcard details and try again'

    @staticmethod
    def get_friendly_error_message(error):
        return 'An error occurred when communicating with the payment gateway.'

    def charge(self, order_number, total, card, currency=settings.STRIPE_CURRENCY,
               description=None, metadata=None, **kwargs):
        logger.info("Authorizing payment on order '%s' via stripe" % (order_number))
        if not card:
            logger.error("Card info not found (no stripe token) for order '%s' while trying to charge stripe" %
                         (order_number))
            raise UnableToTakePayment("Invalid card info")
        try:
            charge_and_capture_together = getattr(settings,
                                                  "STRIPE_CHARGE_AND_CAPTURE_IN_ONE_STEP",
                                                  False)
            stripe_auth_id = stripe.Charge.create(
                    amount=(total.incl_tax * 100).to_integral_value(),
                    currency=currency,
                    card=card,
                    description=description,
                    metadata=(metadata or {'order_number': order_number}),
                    capture=charge_and_capture_together,
                    **kwargs
                ).id
            logger.info("Payment authorized for order %s via stripe." % (order_number))
            return stripe_auth_id
        except stripe.CardError as e:
            logger.exception('Card Error for order: \'{}\''.format(order_number))
            raise UnableToTakePayment(self.get_friendly_decline_message(e))
        except stripe.StripeError as e:
            logger.exception('Stripe Error for order: \'{}\''.format(order_number))
            raise InvalidGatewayRequestError(self.get_friendly_error_message(e))

    def capture(self, order_number, **kwargs):
        """
        if capture is set to false in charge, the charge will only be pre-authorized
        one need to use capture to actually charge the customer
        """
        logger.info("Initiating payment capture for order '%s' via stripe" % (order_number))
        try:
            order = Order.objects.get(number=order_number)
            payment_source = Source.objects.get(order=order)
            # get charge_id from source
            charge_id = payment_source.reference
            # find charge
            charge = stripe.Charge.retrieve(charge_id)
            # capture
            charge.capture()
            # set captured timestamp
            payment_source.date_captured = timezone.now()
            payment_source.save()
            logger.info("payment for order '%s' (id:%s) was captured via stripe (stripe_ref:%s)" %
                        (order.number, order.id, charge_id))
        except Source.DoesNotExist:
            logger.exception('Source Error for order: \'{}\''.format(order_number))
            raise Exception("Capture Failiure could not find payment source for Order %s" %
                            order_number)
        except Order.DoesNotExist:
            logger.exception('Order Error for order: \'{}\''.format(order_number))
            raise Exception("Capture Failiure Order %s does not exist" % order_number)
