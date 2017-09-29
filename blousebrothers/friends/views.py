from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.generic import (
    RedirectView,
    FormView,
)

from blousebrothers.users.models import User
from blousebrothers.auth import BBLoginRequiredMixin

from .models import FriendShipRequest
from .forms import FriendsForm


def ajax_switch(request, attribute):
    """
    Ajax generic switch view.
    """
    status = request.GET['state'] == 'true'
    request.user.gives_friendship.filter(
        to_user_id=request.GET['friend_id']
    ).update(
        **{attribute: status}
    )
    return JsonResponse({'success': True})


def update_sharecards(request):
    return ajax_switch(request, "share_cards")


def update_shareresults(request):
    return ajax_switch(request, "share_results")


def update_shareconfs(request):
    return ajax_switch(request, "share_confs")


class FriendsView(BBLoginRequiredMixin, FormView):
    form_class = FriendsForm
    template_name = 'friends/home.html'
    success_url = reverse_lazy('friends:home')

    def form_valid(self, form):
        for friend in form.cleaned_data['friends']:
            FriendShipRequest.objects.create(requester=self.request.user, target=friend)
            ctx = dict(requester=self.request.user, user=friend)
            msg_plain = render_to_string('friends/emails/friend_request.txt', ctx)
            msg_html = render_to_string('friends/emails/friend_request.html', ctx)
            send_mail(
                    "{} t'invite à rejoindre son groupe d’amis sur BlouseBrothers.".format(self.request.user.username),
                    msg_plain,
                    'noreply@blousebrothers.fr',
                    [friend.email],
                    html_message=msg_html,
            )
        messages.info(self.request, "Demande envoyée !")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(
            offers=self.request.user.friendship_offers.filter(deleted=False, accepted=False),
        )
        return kwargs


class AcceptFriendsView(BBLoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        offer = FriendShipRequest.objects.get(pk=self.request.GET['pk'])
        assert(offer in self.request.user.friendship_offers.all())
        offer.accepted = True
        offer.save()
        self.request.user.add_relationship(offer.requester)
        messages.info(self.request,
                      "Félicitations ! Tu es mantenant ami avec {}.".format(offer.requester.username)
                      )
        ctx = dict(friend=self.request.user, user=offer.requester)
        msg_plain = render_to_string('friends/emails/friend_accept.txt', ctx)
        msg_html = render_to_string('friends/emails/friend_accept.html', ctx)
        send_mail(
                "{} a accepté ta demande d'ajout aux amis sur BlouseBrothers.".format(self.request.user.username),
                msg_plain,
                'noreply@blousebrothers.fr',
                [offer.requester.email],
                html_message=msg_html,
        )
        return reverse("friends:home")


class RefuseFriendsView(BBLoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        offer = FriendShipRequest.objects.get(pk=self.request.GET['pk'])
        assert(offer in self.request.user.friendship_offers.all())
        offer.accepted = False
        offer.save()
        messages.info(self.request,
                      "La demande de {} a été déclinée.".format(offer.requester.username)
                      )
        return reverse("friends:home")


class RemoveFriendsView(BBLoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        friend = User.objects.get(pk=self.request.GET['pk'])
        self.request.user.remove_relationship(friend)
        messages.info(self.request,
                      "{} ne fait plus partie de tes amis.".format(friend.username)
                      )
        return reverse("friends:home")
