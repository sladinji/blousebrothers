import re
from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.views.generic import (
    RedirectView,
    FormView,
    CreateView,
    UpdateView,
    ListView,
)

from blousebrothers.users.models import User
from blousebrothers.auth import BBLoginRequiredMixin
from blousebrothers.tools import bbmail

from .models import FriendShipRequest, Group, MemberShipRequest, GroupInvitRequest
from .forms import FriendsForm, GroupForm, GroupInvitForm


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
            bbmail(
                    "{} t'invite à rejoindre son groupe d’amis sur BlouseBrothers.".format(self.request.user.username),
                    msg_plain,
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


class FriendsListView(BBLoginRequiredMixin, ListView):
    paginate_by = 20
    template_name = "friends/friends_list.html"

    def get_queryset(self):
        qs = self.request.user.friends
        if self.request.GET.get('q', False):
            qs = qs.filter(
                Q(username__icontains=self.request.GET['q']) |
                Q(first_name__icontains=self.request.GET['q']) |
                Q(last_name__icontains=self.request.GET['q'])
            )
        return self.request.user.get_relations(qs)


class GroupView(BBLoginRequiredMixin, FormView):
    form_class = GroupForm
    template_name = 'friends/group.html'
    success_url = reverse_lazy('friends:group')

    def form_valid(self, form):
        for group in form.cleaned_data['groups']:
            MemberShipRequest.objects.get_or_create(requester=self.request.user, target=group)[0]
            ctx = dict(requester=self.request.user, group=group)
            msg_plain = render_to_string('friends/emails/group_request.txt', ctx)
            msg_html = render_to_string('friends/emails/group_request.html', ctx)
            bbmail(
                    "{} souhaiterait rejoindre le groupe '{}'.".format(self.request.user.username, group.name),
                    msg_plain,
                    [user.email for user in group.moderators.all()],
                    html_message=msg_html,
            )
        messages.info(self.request, "Demande envoyée !")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
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
        bbmail(
                "{} a accepté ta demande d'ajout aux amis sur BlouseBrothers.".format(self.request.user.username),
                msg_plain,
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


class GroupCreateView(CreateView):
    model = Group
    fields = ['name']

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.abs    """
        self.object = form.save()
        self.object.moderators.add(self.request.user)
        self.object.members.add(self.request.user)
        return super().form_valid(form)


class GroupUpdateView(BBLoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupInvitForm
    template_name = "friends/group_update.html"

    def get_object(self, queryset=None):
        group = super().get_object(queryset)
        user = self.request.user
        if user not in group.members.all() | group.moderators.all():
            raise PermissionDenied
        return group

    def form_valid(self, form):
        if self.request.user not in self.object.moderators.all():
            raise PermissionDenied
        for match in re.finditer(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", form.cleaned_data['emails']):
            try:
                user = User.objects.get(email=match.group(0))
                if GroupInvitRequest.objects.get_or_create(requester=self.object, target=user)[0].accepted:
                    continue
                ctx = dict(group=self.object, user=user, requester=self.request.user)
                msg_plain = render_to_string('friends/emails/group_invit.txt', ctx)
                msg_html = render_to_string('friends/emails/group_invit.html', ctx)
                bbmail(
                    '{}, tu es invité(e) à rejoindre le groupe "{}"'.format(user.username, self.object.name),
                    msg_plain,
                    [user.email],
                    html_message=msg_html,
                    tags=['GroupInvit']
                )
            except:
                ctx = dict(group=self.object, requester=self.request.user)
                msg_plain = render_to_string('friends/emails/group_invit_new_user.txt', ctx)
                msg_html = render_to_string('friends/emails/group_invit_new_user.html', ctx)
                bbmail(
                        'Invitation pour rejoindre le groupe "{}"'.format(self.object.name),
                        msg_plain,
                        [match.group(0)],
                    html_message=msg_html,
                    tags=['GroupInvitNewUser']
                )
        messages.info(self.request, 'Les invitations sont bien parties !')
        return super().form_valid(form)


class AcceptMemberView(BBLoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        offer = MemberShipRequest.objects.get(pk=self.request.GET['pk'])
        assert(self.request.user in offer.target.moderators.all())
        offer.accepted = True
        offer.save()
        offer.target.members.add(offer.requester)
        messages.info(self.request,
                      '{} a bien été ajouté au groupe "{}".'.format(offer.requester.username, offer.target.name)
                      )
        ctx = dict(group=offer.target, user=offer.requester)
        msg_plain = render_to_string('friends/emails/group_accept.txt', ctx)
        msg_html = render_to_string('friends/emails/group_accept.html', ctx)
        bbmail(
                'Bienvenue dans le groupe "{}"'.format(offer.target.name),
                msg_plain,
                [offer.requester.email],
                html_message=msg_html,
        )
        return offer.target.get_absolute_url()


class AcceptGroupInvit(BBLoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        offer = GroupInvitRequest.objects.get(pk=self.request.GET['pk'])
        assert(self.request.user == offer.target)
        offer.accepted = True
        offer.save()
        offer.requester.members.add(offer.target)
        messages.info(self.request,
                      'Félicitations, tu es maintenant membre du groupe "{}".'.format(offer.requester.name)
                      )
        return offer.requester.get_absolute_url()


class RefuseMemberView(BBLoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        offer = MemberShipRequest.objects.get(pk=self.request.GET['pk'])
        assert(self.request.user in offer.target.moderators.all())
        offer.accepted = False
        offer.save()
        messages.info(self.request,
                      "La demande de {} a été déclinée.".format(offer.requester.username)
                      )
        return reverse("friends:group")


class RefuseGroupInvitView(BBLoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        offer = GroupInvitRequest.objects.get(pk=self.request.GET['pk'])
        assert(self.request.user == offer.target)
        offer.accepted = False
        offer.save()
        messages.info(self.request,
                      "La demande de {} a été déclinée.".format(offer.requester.username)
                      )
        return reverse("friends:group")


class RemoveMemberView(BBLoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        friend = User.objects.get(pk=self.request.GET['user_id'])
        group = Group.objects.get(pk=self.request.GET['group_id'])
        assert(self.request.user in group.moderators.all())
        group.members.remove(friend)
        messages.info(self.request,
                      "{} ne fait plus partie du groupe {}".format(friend.username, group.name)
                      )
        return reverse("friends:group")
