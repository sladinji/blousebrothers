# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.apps import apps

from .models import User
from .forms import UserForm, WalletForm
from blousebrothers.shortcuts.auth import BBRequirementMixin
from mangopay.models import (
    MangoPayNaturalUser,
    MangoPayCardRegistration,
    MangoPayWallet,
)

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')


class UserDetailView(BBRequirementMixin, DetailView):
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

    def get(self, request, *args, **kwargs):
        if 'data' in request.GET:
            mpu = request.user.mangopay_users.first()
            card_registration = mpu.mangopay_card_registrations.order_by('-id').first()
            if card_registration.mangopay_card.mangopay_id:
                raise Exception("Mango pay id already exist ???")
            card_registration.handle_registration_data(request.GET['data'])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if not self.request.user.gave_all_required_info():
            messages.error(self.request, 'Pour être conférencier, vous devez compléter le formulaire ci-dessous.')
        return super().get_context_data(**kwargs)


class UserWalletView(LoginRequiredMixin, UpdateView):

    form_class = WalletForm
    template_name='users/mangopay_form.html'
    success_url='.'

    def get_context_data(self, **kwargs):

        if not self.request.user.gave_all_mangopay_info() :
            return super().get_context_data(**kwargs)

        mangopay_user, mpu_created = MangoPayNaturalUser.objects.get_or_create(user=self.request.user)
        mangopay_user.birthday = self.request.user.birth_date
        mangopay_user.country_of_residence = self.request.user.country_of_residence
        mangopay_user.nationality = self.request.user.nationality
        mangopay_user.save()
        if mpu_created:
            mangopay_user.create()
        # WALLET
        wallet, w_created = MangoPayWallet.objects.get_or_create(mangopay_user=mangopay_user)
        wallet.mangopay_user = mangopay_user
        wallet.save()

        if w_created:
            wallet.create(description="{}'s Wallet".format(self.request.user.username))
        # CARD REGISTRATION

        card_registration, cr_created = MangoPayCardRegistration.objects.get_or_create(mangopay_user=mangopay_user)
        if cr_created:
            card_registration.create("EUR")
        pd = card_registration.get_preregistration_data()

        if 'errorCode' in self.request.GET:
            messages.error(self.request, self.request.GET['errorCode'])

        return super().get_context_data(wallet=wallet, mangopay_user=mangopay_user,
                                        card_registration=card_registration,
                                        card=pd, balance=wallet.balance(), **kwargs)

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class Subscription(TemplateView):
    template_name = 'pages/subscription.html'

    def get(self, request, *args, **kwargs):
        """
        Display subscriptions page or redirect to basket if subscription was clicked.
        """
        if kwargs['sub_id']:
            sub = Product.objects.get(id=kwargs['sub_id'])
            request.basket.add_product(sub, 1)
            return redirect('/basket/')
        return super().get(request, *args, **kwargs)
