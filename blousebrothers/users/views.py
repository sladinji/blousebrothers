# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal

from django.apps import apps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView, FormView
from django.http import HttpResponseRedirect
from django.db.utils import IntegrityError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from invitations.models import Invitation
from blousebrothers.auth import BBLoginRequiredMixin, MangoPermissionMixin

from .models import User
from .forms import (
    UserForm,
    PayInForm,
    CardRegistrationForm,
    EmailInvitationForm,
    UserSmallerForm,
    IbanForm,
    PayOutForm,
)
from mangopay.models import (
    MangoPayCardRegistration,
    MangoPayPayInByCard,
)
from blousebrothers.tools import get_full_url, check_bonus

Product = apps.get_model('catalogue', 'Product')
ProductClass = apps.get_model('catalogue', 'ProductClass')


class UserDetailView(DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(BBLoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(BBLoginRequiredMixin, UpdateView):
    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        """
        Call handle bonus if new info allow to create mangopay wallet.
        """
        super().form_valid(form)
        check_bonus(self.request)
        return HttpResponseRedirect(self.get_success_url())

    def get_form_class(self):
        if self.request.user.gave_all_mangopay_info:
            return UserForm
        else:
            return UserSmallerForm


class UserSendInvidation(BBLoginRequiredMixin, FormView):
    form_class = EmailInvitationForm

    def form_valid(self, form):
        try:
            invite = Invitation.create(form.cleaned_data["email"], inviter=self.request.user)
            invite.send_invitation(self.request)
            messages.success(self.request, "L'invitation à bien été envoyée à"
                             " {}.".format(form.cleaned_data["email"]))
        except IntegrityError:
            messages.error(self.request, "L'invitation n'a pas été envoyée car"
                           " {} a déjà été parrainé.".format(
                               form.cleaned_data["email"])
                           )
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.POST['current_url']


class Needs3DS(Exception):
    pass


class BaseWalletFormView(MangoPermissionMixin, FormView):

    def get_success_url(self):
        return reverse('users:wallet')


class UserWalletView(BaseWalletFormView):

    template_name = 'users/wallet.html'
    form_class = PayInForm

    def get(self, request, *args, **kwargs):
        if 'transactionId' in request.GET:
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

        check_bonus(request)
        return super().get(request, *args, **kwargs)

    def handle_payin_status(self, payin):
        if payin.status == 'SUCCEEDED':
            messages.success(
                self.request,
                'Le transfert de {} a bien été pris en compte (référence : {})'.format(
                    payin.debited_funds, payin.mangopay_id)
            )
            ctx = dict(payin=payin, user=self.request.user)
            msg_plain = render_to_string('confs/email/confirm_credit.txt', ctx)
            msg_html = render_to_string('confs/email/confirm_credit.html', ctx)
            send_mail(
                    'Confirmation Crédit [réf. {}]'.format(payin.mangopay_id),
                    msg_plain,
                    'noreply@blousebrothers.fr',
                    [self.request.user.email],
                    html_message=msg_html,
            )
        else:
            messages.error(self.request,
                           'Le paiement a échoué (référence : {})'.format(
                               payin.mangopay_id)
                           )

    def payin(self, credit, request):
        payin = MangoPayPayInByCard()
        mangopay_user = self.request.user.mangopay_user
        payin.mangopay_user = mangopay_user
        wallet = self.request.user.wallet
        if self.request.user.is_superuser:
            wallet = self.request.user.wallet_bonus
        payin.mangopay_wallet = wallet
        if 'card_id' in request.POST:
            if not request.POST['card_id']:
                # safari does not handle required html tag...
                messages.error(self.request, 'Tu dois sélectionner une carte de paiement.')
                return
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


class AddIbanView(BaseWalletFormView):
    form_class = IbanForm
    template_name = 'users/addiban_form.html'
    msg_access_denied = 'Merci de compléter le formulaire ci-dessous pour pouvoir ajouter un RIB.'

    def form_valid(self, form):
        self.request.user.create_bank_account(
            form.cleaned_data['iban'],
            form.cleaned_data['bic']
        )
        return super().form_valid(form)


class PayOutView(BaseWalletFormView):
    form_class = PayOutForm
    template_name = 'users/payout_form.html'

    def form_valid(self, form):
        payout = self.request.user.payout(form.cleaned_data['debited_funds'])
        if payout.status == 'CREATED':
            messages.success(self.request,
                             "Le retrait de {} € est validé, le transfert devrait être effectif sous peu.".format(
                                 form.cleaned_data["debited_funds"],
                             )
                             )
            ctx = dict(payout=payout, user=self.request.user)
            msg_plain = render_to_string('confs/email/confirm_payout.txt', ctx)
            msg_html = render_to_string('confs/email/confirm_payout.html', ctx)
            send_mail(
                    'Confirmation Retrait [réf. {}]'.format(payout.mangopay_id),
                    msg_plain,
                    'noreply@blousebrothers.fr',
                    [self.request.user.email],
                    html_message=msg_html,
            )
        else:
            messages.error(self.request,
                           'Le transfert a échoué (référence : {})'.format(
                               payout.mangopay_id)
                           )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(max_value=self.request.user.wallet.balance().amount)
        return kwargs


class AddCardView(BaseWalletFormView):
    """
    Card information are directly sent to MangoPay. This view just display
    a form that send data to MangoPay.
    """
    form_class = PayInForm
    template_name = 'users/addcard_form.html'

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
                                        card=pd,
                                        cr_form=cr_form, **kwargs)


class Subscription(BBLoginRequiredMixin, TemplateView):
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
