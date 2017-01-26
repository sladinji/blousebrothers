from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from oscar.apps.basket.views import BasketAddView as CoreBasketAddView
from oscar.core.loading import get_class
from blousebrothers.confs.models import Test
from blousebrothers.users.models import Sale
from money import Money
from mangopay.models import MangoPayTransfer

BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')
selector = get_class('partner.strategy', 'Selector')()


class MangoTransfertException(Exception):
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
            return HttpResponseRedirect(reverse("account_signup"))
        if not self.request.user.gave_all_mangopay_info():
            messages.warning(self.request, _("Merci de compléter ce formulaire pour pouvoir continuer"),
                             extra_tags='safe noicon')
            return HttpResponseRedirect(reverse("users:update") + '?next={}'.format(self.request.path))

        test, created = Test.objects.get_or_create(conf=form.product.conf, student=self.request.user)

        if created:
            return self.debit_wallet(form, test)

        return self.redirect_success(form)

    def debit_wallet(self, form, test):
        """
        Debit user wallet according to given test and redirect to user according to transfer result.
        """
        info = selector.strategy().fetch_for_product(form.product)

        if info.price.excl_tax == 0:
            return self.redirect_success(form)

        transfer = MangoPayTransfer()
        transfer.mangopay_credited_wallet = form.product.conf.owner.wallet
        transfer.mangopay_debited_wallet = self.request.user.wallet
        transfer.debited_funds = info.price.excl_tax
        transfer.save()
        fees = info.price.excl_tax * Decimal('0.1')
        transfer.create(fees=Money(fees, str(transfer.debited_funds.currency)))
        if transfer.status == "FAILED":
            test.delete()
            if transfer.result_code == "001001":
                messages.error(self.request, _("Merci de créditer ton compte pour pouvoir faire cette conférence (prix : {})").format(info.price.excl_tax),
                               extra_tags='safe noicon')
                return HttpResponseRedirect(reverse("users:wallet") + '?next={}'.format(self.request.path))
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
            test.delete()
            raise MangoTransfertException(
                "status : {status}result_code : {result_code} mangopay_id : {mangopay_id}".format(
                    transfer.__dict__
                )
            )

    def get_success_url(self, product=None):
        return reverse('confs:test', kwargs={"slug": product.conf.slug})

    def redirect_success(self, form):
        messages.success(self.request, self.get_success_message(form),
                         extra_tags='safe noicon')
        # Send signal for basket addition
        self.add_signal.send(
            sender=self, product=form.product, user=self.request.user,
            request=self.request)
        return HttpResponseRedirect(self.get_success_url(form.product))
