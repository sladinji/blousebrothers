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

from .models import User
from .forms import UserForm, PayInForm, CardRegistrationForm
from mangopay.models import (
    MangoPayNaturalUser,
    MangoPayCardRegistration,
    MangoPayWallet,
    MangoPayPayInByCard,
)

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


class UserWalletView(LoginRequiredMixin, FormView):

    template_name = 'users/mangopay_form.html'
    success_url = '.'
    form_class = PayInForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.gave_all_mangopay_info():
            messages.error(self.request, 'Merci de compléter le formulaire ci-dessous '
                           'pour pouvoir créditer ton compte.')
            return redirect('users:update')
        elif 'data' in request.GET:
            mpu = request.user.mangopay_users.first()
            card_registration = mpu.mangopay_card_registrations.order_by('-id').first()
            if card_registration.mangopay_card.mangopay_id:
                raise Exception("Mango pay id already exist ???")
            card_registration.handle_registration_data(request.GET['data'])
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'sub_credit' in request.POST:
            credit = request.POST['credit']
            print(credit)
            payin = MangoPayPayInByCard()
            mangopay_user = MangoPayNaturalUser.objects.get(user=self.request.user)
            payin.mangopay_user = mangopay_user
            payin.mangopay_wallet = MangoPayWallet.objects.get(mangopay_user=mangopay_user)
            payin.mangopay_card = mangopay_user.mangopay_card_registrations.first().mangopay_card
            payin.debited_funds = Decimal(credit)
            payin.fees = 0
            payin.create(secure_mode_return_url='https://blousebrothers.fr')
        return self.get(request, *args, **kwargs)

    def get_card_registration(self):
        card_registration, cr_created = MangoPayCardRegistration.objects.get_or_create(
            mangopay_user=self.request.user.mangopay_user
        )
        if cr_created:
            card_registration.create("EUR")
            pd = card_registration.get_preregistration_data()
            pd.update(data=pd['preregistrationData'], accessKeyRef=pd['accessKey'])
            returnURL = "https://" if self.request.is_secure() else "http://"
            returnURL += self.request.get_host() + reverse('users:wallet')
            pd.update(returnURL=returnURL)
            cr_form = CardRegistrationForm(initial=pd)
        else:
            card_registration.mangopay_card.request_card_info()
            cr_form = None
            pd = None
        return card_registration, cr_form, pd

    def get_context_data(self, **kwargs):
        card_registration, cr_form, pd = self.get_card_registration()

        if 'errorCode' in self.request.GET:
            messages.error(self.request, self.request.GET['errorCode'])

        return super().get_context_data(wallet=self.request.user.wallet,
                                        mangopay_user=self.request.user.mangopay_user,
                                        card_registration=card_registration,
                                        card=pd, balance=self.request.user.wallet.balance(),
                                        no_card_registred=card_registration.mangopay_card.mangopay_id==None,
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
