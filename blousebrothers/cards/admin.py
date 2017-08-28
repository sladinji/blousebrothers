from django.contrib import admin

# Register your models here.
from blousebrothers.cards.models import Card, Deck


class CardAdmin(admin.ModelAdmin):
    list_display = ('content',)
    list_filter = ('specialities', 'items',)
    filter_horizontal = ['items', 'specialities']
    search_fields = ['content', ]
    list_editable = ('content',)


admin.site.register(Card, CardAdmin)
admin.site.register(Deck)
