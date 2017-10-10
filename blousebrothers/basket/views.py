from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from django.shortcuts import redirect
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from oscar.apps.basket.views import BasketAddView as CoreBasketAddView
from oscar.apps.basket.views import BasketView as CoreBasketView
from oscar.apps.basket.views import VoucherAddView as CoreVoucherAddView
from oscar.core.loading import get_class
from blousebrothers.confs.models import Test
from blousebrothers.users.models import Sale
from money import Money
from mangopay.models import MangoPayTransfer
from oscar.apps.shipping.methods import NoShippingRequired
from django.apps import apps
from blousebrothers.tools import get_full_url


BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')
selector = get_class('partner.strategy', 'Selector')()
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
SubscriptionType = apps.get_model('confs', 'SubscriptionType')
Subscription = apps.get_model('confs', 'Subscription')


class BasketView(CheckoutSessionMixin, CoreBasketView):
    def get_context_data(self, **kwargs):
        self.checkout_session.use_shipping_method(
                            NoShippingRequired().code)
        kwargs.update(stripe_publishable_key=settings.STRIPE_PUBLISHABLE_KEY)
        for line in self.request.basket.all_lines():
            try:
                if line.product.categories.first().name == '__Abonnements':
                    return super(BasketView, self).get_context_data(selected_sub_id=line.product.id, **kwargs)
            except:
                pass
        return super(BasketView, self).get_context_data(selected_sub_id=None, **kwargs)


class MangoTransfertException(Exception):
    pass


class MangoNoEnoughCredit(Exception):
    pass


class BasketAddView(CoreBasketAddView):
    """
    Debit user wallet if product is a conference.
    """

    def form_valid(self, form):
        if not form.product.conf:
            return super().form_valid(form)
        if self.request.user.is_anonymous():
            messages.warning(self.request, _("Merci de te connecter pour pouvoir faire un dossier"),
                             extra_tags='safe noicon')
            return HttpResponseRedirect(reverse("home"))
        free_conf = form.product.conf.owner.username == "BlouseBrothers"
        if not free_conf and not self.request.user.gave_all_mangopay_info:
            messages.success(self.request, _("Merci de compléter ce formulaire pour pouvoir continuer"),
                             extra_tags='safe noicon')
            return HttpResponseRedirect(reverse("users:update") + '?next={}'.format(self.request.path))

        test, created = Test.objects.get_or_create(conf=form.product.conf, student=self.request.user)

        if created and not free_conf:
            try:
                if self.request.user.subscription \
                        and self.request.user.subscription.type.product.attr.access_confs \
                        or self.request.user.has_friendship.filter(
                            from_user=form.product.conf.owner,
                            share_confs=True,
                        ).exists():
                    if self.request.user.subscription and self.request.user.subscription.price_paid > 0:
                        # Do not create sale for user with subscription price = O (référents...)
                        Sale.objects.create(
                            conferencier=form.product.conf.owner,
                            student=self.request.user,
                            product=form.product,
                            conf=form.product.conf,
                        )
                    self.request.user.conf_encours_url = get_full_url(
                        self.request, 'confs:test', args=(form.product.conf.slug,)
                    )
                    self.request.user.save()
                    return self.redirect_success(form)
                else:
                    return self.debit_wallet(form, test, self.request.user.wallet_bonus)
            except Exception as ex:
                try:
                    return self.debit_wallet(form, test, self.request.user.wallet)
                except MangoNoEnoughCredit:
                    msg = _("Merci de choisir un abonnement.")
                    messages.success(self.request, msg, extra_tags='safe noicon')
                    test.delete()
                    return HttpResponseRedirect(
                        reverse("users:subscription",
                                kwargs={'sub_id': 0}) + '?next={}'.format(self.request.path)
                    )
                except Exception as ex:
                    test.delete()
                    raise ex

        return self.redirect_success(form)

    def debit_wallet(self, form, test, debited_wallet):
        """
        Debit user wallet according to given test.
        """
        info = selector.strategy().fetch_for_product(form.product)

        if info.price.excl_tax == 0:
            return self.redirect_success(form)

        transfer = MangoPayTransfer()
        transfer.mangopay_credited_wallet = form.product.conf.owner.wallet
        transfer.mangopay_debited_wallet = debited_wallet
        transfer.debited_funds = info.price.excl_tax
        transfer.save()
        if test.conf.no_fees:
            fees = 0
        else:
            fees = info.price.excl_tax * Decimal('0.3')
            fees = fees.quantize(Decimal('0.01'), ROUND_HALF_UP)
        transfer.create(fees=Money(fees, str(transfer.debited_funds.currency)))
        if transfer.status == "FAILED":
            if transfer.result_code == "001001":
                raise MangoNoEnoughCredit(info.price.excl_tax)
            else:
                raise MangoTransfertException(
                    "status : {status}result_code : {result_code} mangopay_id : {mangopay_id}".format(
                        transfer.__dict__
                    )
                )
        elif transfer.status == "SUCCEEDED":
            Sale.objects.create(
                conferencier=form.product.conf.owner,
                student=self.request.user,
                transfer=transfer,
                credited_funds=info.price.excl_tax - fees,
                fees=fees,
                product=form.product,
                conf=form.product.conf,
            )
            return self.redirect_success(form)
        else:
            raise MangoTransfertException(
                "status : {status}result_code : {result_code} mangopay_id : {mangopay_id}".format(
                    transfer.__dict__
                )
            )

    def get_success_url(self, product=None):
        if product and product.conf:
            self.request.user.status = "buyer_ok"
            self.request.user.save()
            product.conf.owner.status = 'conf_sold'
            product.conf.owner.save()
            return reverse('confs:test', kwargs={"slug": product.conf.slug})
        else:
            return super().get_success_url(product)

    def redirect_success(self, form):
        messages.success(self.request, self.get_success_message(form),
                         extra_tags='safe noicon')

        # Send signal for basket addition
        self.add_signal.send(
            sender=self, product=form.product, user=self.request.user,
            request=self.request)
        return HttpResponseRedirect(self.get_success_url(form.product))


class VoucherAddView(CoreVoucherAddView):

    def form_valid(self, form):
        code = form.cleaned_data['code']
        if code == "ECNIMEMO3" and not self.request.user.subscription:
            subtype = SubscriptionType.objects.get(name="Fiches")
            sub = Subscription(user=self.request.user, type=subtype)
            sub.date_over = date(2017, 12, 31)
            sub.price_paid = 0
            sub.save()
            messages.info(self.request, _("Bien reçu! Enjoy :-)"),
                          extra_tags='safe noicon')
            return redirect(reverse('cards:home'))
        return super().form_valid(form)


