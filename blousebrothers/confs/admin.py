from django.contrib import admin
from .models import Conference, Item, Question, Speciality, QuestionImage, ItemKeyWord
import nested_admin
# Register your models here.


class QuestionImageInline(nested_admin.NestedTabularInline):
    model = QuestionImage
    exclude = ['order', 'date_created']
    extra = 1


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    exclude = ['order']
    inlines = [QuestionImageInline]
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionImageInline]

class ItemKWInlne(nested_admin.NestedTabularInline):
    model = ItemKeyWord

class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemKWInlne,]

class ConferenceAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'summary', 'owner')
    inlines = [QuestionInline, ]
    exclude = ['owner', 'summary', 'type']

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()

admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Speciality)
admin.site.register(Question, QuestionAdmin)
