from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import (
    RedirectView,
    FormView,
)

from blousebrothers.users.models import User
from blousebrothers.auth import BBLoginRequiredMixin

from .models import FriendShipRequest
from .forms import FriendsForm


def update_sharecards(request):
    """
    Ajax view.
    """
    status = request.GET['state'] == 'true'
    request.user.from_people.filter(
        to_user_id=request.GET['friend_id']
    ).update(
        share_cards=status
    )
    return JsonResponse({'success': True})


def update_shareresults(request):
    """
    Ajax view.
    """
    status = request.GET['state'] == 'true'
    request.user.from_people.filter(
        to_user_id=request.GET['friend_id']
    ).update(
        share_results=status,
    )
    return JsonResponse({'success': True})


class FriendsView(BBLoginRequiredMixin, FormView):
    form_class = FriendsForm
    template_name = 'friends/home.html'
    success_url = reverse_lazy('friends:home')

    def form_valid(self, form):
        for friend in form.cleaned_data['friends']:
            FriendShipRequest.objects.create(requester=self.request.user, target=friend)

        messages.info(self.request, "Demandes envoyées !")
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
                      "Félicitations ! Tu es mantenant ami avec {}."
                      " Chacun a maintenant accès aux fiches de l'autre.".format(offer.requester.username)
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
