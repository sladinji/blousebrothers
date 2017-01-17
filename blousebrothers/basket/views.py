from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from oscar.apps.basket.views import BasketAddView as CoreBasketAddView
from oscar.core.loading import get_class
from blousebrothers.confs.models import Test
from blousebrothers.users.models import Transaction
from money import Money
from mangopay.models import MangoPayTransfer

BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')
selector = get_class('partner.strategy', 'Selector')()


class BasketAddView(CoreBasketAddView):

    def form_valid(self, form):
        if not form.product.conf:
            return super().form_valid(form)
        # offers_before = self.request.basket.applied_offers()
        if self.request.user.is_anonymous():
            messages.success(self.request, _("Vous devez vous connecter pour faire un dossier"),
                             extra_tags='safe noicon')
            return HttpResponseRedirect(reverse("account_signup"))

        __, created = Test.objects.get_or_create(conf=form.product.conf, student=self.request.user)

        if created:
            info = selector.strategy().fetch_for_product(form.product)
            transfer = MangoPayTransfer()
            transfer.mangopay_credited_wallet = form.product.conf.owner.wallet
            transfer.mangopay_debited_wallet = self.request.user.wallet
            transfer.debited_funds = info.price.incl_tax
            transfer.save()
            fees = info.price.incl_tax * Decimal('0.1')

            transfer.create(fees=Money(fees, str(transfer.debited_funds.currency)))
            Transaction.objects.create(
                conferencier=form.product.conf.owner,
                student=self.request.user,
                transfer=transfer,
                credited_funds=info.price.incl_tax - fees,
                fees=fees,
                product=form.product,
            )

        # self.request.basket.add_product(
        #    form.product, form.cleaned_data['quantity'],
        #    form.cleaned_options())

        messages.success(self.request, self.get_success_message(form),
                         extra_tags='safe noicon')

        # Check for additional offer messages
        # BasketMessageGenerator().apply_messages(self.request, offers_before)

        # Send signal for basket addition
        self.add_signal.send(
            sender=self, product=form.product, user=self.request.user,
            request=self.request)

        return HttpResponseRedirect(self.get_success_url(form.product))

    def get_success_url(self, product=None):
        return reverse('confs:test', kwargs={"slug": product.conf.slug})
