from django.db import models


class FriendShipRequest(models.Model):
    requester = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_requests')
    target = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_offers')
    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)


class Relationship(models.Model):
    from_user = models.ForeignKey('users.User', related_name='from_people')
    to_user = models.ForeignKey('users.User', related_name='to_people')
    share_cards = models.BooleanField(default=True)
    share_results = models.BooleanField(default=True)

    def __repr__(self):
        return "<{0.from_user} --> {0.to_user}, cards : {0.share_cards}, results : {0.share_results}>".format(self)
