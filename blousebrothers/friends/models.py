from django.db import models


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

