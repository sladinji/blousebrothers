# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal

from django.apps import apps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView, FormView
from django.http import HttpResponseRedirect

from .models import User
from .forms import UserForm, PayInForm, CardRegistrationForm
from mangopay.models import (
    MangoPayNaturalUser,
    MangoPayCardRegistration,
    MangoPayWallet,
    MangoPayPayInByCard,
)
from blousebrothers.tools import get_full_url

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')


class UserDetailView(DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    form_class = UserForm

    # we already imported User in the view code above, remember?

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class Needs3DS(Exception):
    pass


class UserWalletView(LoginRequiredMixin, FormView):

    template_name = 'users/wallet.html'
    success_url = '.'
    form_class = PayInForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.gave_all_mangopay_info():
            messages.error(self.request, 'Merci de compléter le formulaire ci-dessous '
                           'pour pouvoir créditer ton compte.')
            return redirect('users:update')

        elif 'transactionId' in request.GET:
            # handle 3DS redirection
            payin = MangoPayPayInByCard.objects.get(mangopay_id=request.GET['transactionId'])
            payin.get()
            self.handle_payin_status(payin)

        elif 'data' in request.GET:
            # handle mango redirection after new card added
            mpu = request.user.mangopay_users.first()
            card_registration = mpu.mangopay_card_registrations.order_by('-id').first()
            if card_registration.mangopay_card.mangopay_id:
                raise Exception("Mango pay id already exist ???")
            card_registration.handle_registration_data(request.GET['data'])
            return redirect(reverse('users:wallet'))

        elif not request.user.has_at_least_one_card and not request.user.is_conferencier:
            return redirect(reverse('users:addcard'))

        return super().get(request, *args, **kwargs)

    def handle_payin_status(self, payin):
        if payin.status == 'SUCCEEDED':
            messages.success(
                self.request,
                'Le paiement de {}€ a bien été pris en compte (référence : {})'.format(
                    payin.debited_funds, payin.mangopay_id)
            )
        else:
            messages.error(self.request,
                           'Le paiement a échoué (référence : {})'.format(
                               payin.mangopay_id)
                           )

    def payin(self, credit, request):
        payin = MangoPayPayInByCard()
        mangopay_user = MangoPayNaturalUser.objects.get(user=self.request.user)
        payin.mangopay_user = mangopay_user
        payin.mangopay_wallet = MangoPayWallet.objects.get(mangopay_user=mangopay_user)
        if 'card_id' in request.POST:
            payin.mangopay_card = mangopay_user.mangopay_card_registrations.get(
                mangopay_card__id=request.POST['card_id']
            ).mangopay_card
        else:
            payin.mangopay_card = mangopay_user.mangopay_card_registrations.exclude(
                mangopay_card__mangopay_id__isnull=True
            ).first().mangopay_card
        payin.debited_funds = Decimal(credit)
        payin.fees = 0
        payin.create(secure_mode_return_url=get_full_url(request, 'users:wallet'))

        if payin.secure_mode_redirect_url:
            raise Needs3DS(payin)

        self.handle_payin_status(payin)

    def post(self, request, *args, **kwargs):
        credit = None

        for x in [5, 10, 15, 20]:
            if 'sub_credit_{}'.format(x) in request.POST:
                credit = x
                break

        if not credit and 'sub_credit' in request.POST:
            credit = request.POST['credit']

        try:
            self.payin(credit, request)
        except Needs3DS as ex:
            return HttpResponseRedirect(ex.args[0].secure_mode_redirect_url)

        return self.get(request, *args, **kwargs)


class AddCardView(LoginRequiredMixin, FormView):
    form_class = PayInForm
    template_name = 'users/addcard_form.html'

    def get_success_url(self):
        return reverse('users:wallet')

    def get_card_registration(self):
        card_registration = MangoPayCardRegistration.objects.create(
            mangopay_user=self.request.user.mangopay_user
        )
        card_registration.create("EUR")
        pd = card_registration.get_preregistration_data()
        pd.update(data=pd['preregistrationData'], accessKeyRef=pd['accessKey'])
        returnURL = "https://" if self.request.is_secure() else "http://"
        returnURL += self.request.get_host() + reverse('users:wallet')
        pd.update(returnURL=returnURL)
        cr_form = CardRegistrationForm(initial=pd)
        return card_registration, cr_form, pd

    def get_context_data(self, **kwargs):
        card_registration, cr_form, pd = self.get_card_registration()

        if 'errorCode' in self.request.GET:
            messages.error(self.request, self.request.GET['errorCode'])

        return super().get_context_data(wallet=self.request.user.wallet,
                                        mangopay_user=self.request.user.mangopay_user,
                                        card_registration=card_registration,
                                        card=pd, balance=self.request.user.wallet.balance(),
                                        cr_form=cr_form, **kwargs)

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class Subscription(LoginRequiredMixin, TemplateView):
    template_name = 'pages/subscription.html'
    permission_denied_message = _("Merci de t'identifier ou de créer un compte pour soucrire à un abonnement")

    def handle_no_permission(self):
        messages.info(self.request, self.permission_denied_message)
        return super().handle_no_permission()

    def get_login_url(self):
        return reverse("account_signup")

    def get(self, request, *args, **kwargs):
        """
        Display subscriptions page or redirect to basket if subscription was clicked.
        """
        if kwargs['sub_id']:
            sub = Product.objects.get(id=kwargs['sub_id'])
            request.basket.add_product(sub, 1)
            return redirect('/basket/')
        return super().get(request, *args, **kwargs)
