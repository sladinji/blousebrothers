from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from oscar.apps.basket.views import BasketAddView as CoreBasketAddView
from oscar.core.loading import get_class
from blousebrothers.confs.models import Test

BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')


class BasketAddView(CoreBasketAddView):

    def form_valid(self, form):
        if not form.product.conf:
            return super().form_valid(form)
        # offers_before = self.request.basket.applied_offers()
        if self.request.user.is_anonymous():
            messages.success(self.request, _("Vous devez vous connecter pour faire un dossier"),
                             extra_tags='safe noicon')
            return HttpResponseRedirect(reverse("account_signup"))

        Test.objects.get_or_create(conf=form.product.conf, student=self.request.user)

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
