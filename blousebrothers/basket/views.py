from django.contrib import messages
from django.http import HttpResponseRedirect
from oscar.apps.basket.views import BasketAddView as CoreBasketAddView
from oscar.core.loading import get_class
from blousebrothers.confs.models import Test

BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')


class BasketAddView(CoreBasketAddView):

    def form_valid(self, form):
        offers_before = self.request.basket.applied_offers()

        Test.objects.create(conf=form.product.conf, student=self.request.user)
        print("YES PAPA!!"*100)

        #self.request.basket.add_product(
        #    form.product, form.cleaned_data['quantity'],
        #    form.cleaned_options())

        messages.success(self.request, self.get_success_message(form),
                         extra_tags='safe noicon')

        # Check for additional offer messages
        BasketMessageGenerator().apply_messages(self.request, offers_before)

        # Send signal for basket addition
        self.add_signal.send(
            sender=self, product=form.product, user=self.request.user,
            request=self.request)

        return HttpResponseRedirect(self.get_success_url())
