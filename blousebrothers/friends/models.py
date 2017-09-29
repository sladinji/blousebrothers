from django.db import models


class FriendShipRequest(models.Model):
    requester = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_requests')
    target = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_offers')
    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)


class Relationship(models.Model):
    from_user = models.ForeignKey('users.User', related_name='gives_friendship')
    to_user = models.ForeignKey('users.User', related_name='has_friendship')
    share_cards = models.BooleanField(default=True)
    share_results = models.BooleanField(default=True)
    share_confs = models.BooleanField(default=True)

    def __repr__(self):
        text = "<{0.from_user} --> {0.to_user}, cards : {0.share_cards}, "
        text += "results : {0.share_results}, confs: {0.share_confs}>"
        return text.format(self)
