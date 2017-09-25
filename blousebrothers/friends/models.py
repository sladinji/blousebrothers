from django.db import models


class FriendShipRequest(models.Model):
    requester = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_requests')
    target = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='friendship_offers')
    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
