from django.contrib import admin

# Register your models here.
from blousebrothers.cards.models import Card, Deck

admin.site.register(Card)
admin.site.register(Deck)
