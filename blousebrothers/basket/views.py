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
            return HttpResponseRedirect(reverse("account_login"))
        free_conf = form.product.conf.owner.username == "BlouseBrothers"

        test, created = Test.objects.get_or_create(conf=form.product.conf, student=self.request.user)

        if created and not free_conf:
            try:
                if self.request.user.subscription \
                        or self.request.user.customer.has_active_subscription() \
                        or self.request.user.has_friendship.filter(
                            from_user=form.product.conf.owner,
                            share_confs=True,
                        ).exists() \
                        or form.product.conf.owner.bbgroups.filter(
                            id__in=self.request.user.bbgroups.all()
                        ).exists():
                    if self.request.user.subscription and self.request.user.subscription.price_paid > 0 \
                            or self.request.user.customer.subscription.plan.amount > 0:
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
                    msg = _("Merci de souscrire un abonnement.")
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
        #  code = form.cleaned_data['code']
        #  if code == "ECNIMEMO3" or code == "ECNIMEMO3M" and not self.request.user.subscription:
        #      subtype = SubscriptionType.objects.get(name="Fiches")
        #      sub = Subscription(user=self.request.user, type=subtype)
        #      sub.date_over = date(2017, 12, 31)
        #      sub.price_paid = 0
        #      sub.save()
        #      messages.info(self.request, _("Bien reçu! Enjoy :-)"),
        #                    extra_tags='safe noicon')
        #      return redirect(reverse('cards:home'))
        return super().form_valid(form)


