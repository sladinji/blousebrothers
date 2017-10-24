from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.db import models
from image_cropping import ImageCropField, ImageRatioField

from blousebrothers.confs.models import Conference


class FriendShipRequest(models.Model):
    requester = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_requests')
    target = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_offers')
    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        txt = "{0.requester} -> {0.target} ({0.create_timestamp}, accepted: {0.accepted},"
        txt += "deleted: {0.deleted})"
        return txt.format(self)


class Relationship(models.Model):
    from_user = models.ForeignKey('users.User', related_name='gives_friendship')
    to_user = models.ForeignKey('users.User', related_name='has_friendship')
    share_cards = models.BooleanField(default=True)
    share_results = models.BooleanField(default=True)
    share_confs = models.BooleanField(default=True)

    def __repr__(self):
        txt = "<{0.from_user} --> {0.to_user}, cards : {0.share_cards}, "
        txt += "results : {0.share_results}, confs: {0.share_confs}>"
        return txt.format(self)

    def __str__(self):
        txt = "{0.from_user} --> {0.to_user}, cards : {0.share_cards}, "
        txt += "results : {0.share_results}, confs: {0.share_confs}"
        return txt.format(self)


class MemberShipRequest(models.Model):
    requester = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='membership_requests')
    target = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='membership_requests')
    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        txt = "{0.requester} -> {0.target} ({0.create_timestamp}, accepted: {0.accepted},"
        txt += "deleted: {0.deleted})"
        return txt.format(self)


class GroupInvitRequest(models.Model):
    target = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='group_invits')
    requester = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='invited_users')
    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        txt = "{0.requester} -> {0.target} ({0.create_timestamp}, accepted: {0.accepted},"
        txt += "deleted: {0.deleted})"
        return txt.format(self)


def group_avatar_path(group, filename):
    return '{0}/images/{1}'.format(group.name, filename)


class Group(models.Model):
    moderators = models.ManyToManyField('users.User', related_name='groups_moderator')
    members = models.ManyToManyField('users.User', related_name='bbgroups')
    name = models.CharField(_("Nom du groupe"), max_length=512, null=False, blank=False,
                            unique=True,
                            help_text=_("Tu peux par exemple entrer le nom de ta corpo :)")
                            )
    avatar = ImageCropField(_("Avatar"), upload_to=group_avatar_path, max_length=255, null=True)
    cropping = ImageRatioField('avatar', '430x360', free_crop=True)
    university = models.ForeignKey('users.University', blank=True, null=True, verbose_name=_("Ville"))

    def __str__(self):
        if self.university:
            return "{0.name} ({0.university})".format(self)
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('friends:group_detail', kwargs={'pk': self.id})

    def nb_members(self):
        return self.members.count() + self.moderators.count()

    @property
    def active_requests(self):
        return self.membership_requests.filter(accepted=False, deleted=False)

    @property
    def shared_confs(self):
        return Conference.objects.filter(
            Q(owner__in=self.members.all()) | Q(owner__in=self.moderators.all()),
            edition_progress=100,
        )
