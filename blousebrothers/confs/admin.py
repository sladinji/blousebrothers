from django.contrib import admin
from .models import (
    Conference, Item, Question, Speciality, QuestionImage, ItemKeyWord, ConferenceImage,
    Answer, Test, TestAnswer
)
import nested_admin
from image_cropping import ImageCroppingMixin
# Register your models here.


class AnswerInline(ImageCroppingMixin, nested_admin.NestedTabularInline):
    model = Answer
    exclude = ['answer', 'explaination']
    extra = 1


class QuestionImageInline(ImageCroppingMixin, nested_admin.NestedTabularInline):
    model = QuestionImage
    exclude = ['order', 'date_created']
    extra = 1


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    exclude = ['question']
    inlines = [QuestionImageInline, AnswerInline]
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionImageInline]


class ItemKWInlne(nested_admin.NestedTabularInline):
    model = ItemKeyWord


class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemKWInlne]


class ConferenceImage(ImageCroppingMixin, nested_admin.NestedTabularInline):
    model = ConferenceImage
    exclude = []
    extra = 1


class ConferenceAdmin(ImageCroppingMixin, nested_admin.NestedModelAdmin):
    list_display = ('title', 'summary', 'owner', 'edition_progress', 'deleted', 'for_sale')
    list_filter = ('deleted', 'for_sale', 'edition_progress')
    inlines = [ConferenceImage, QuestionInline, ]
    exclude = ['summary', 'type']
    filter_horizontal = ['items', 'specialities']
    search_fields = ['summary', 'title', 'questions__answers__answer', 'questions__answers__explaination']

    def get_queryset(self, request):
        """
        Change default model manager to see deleted conference in Admin.
        """
        return Conference.all_objects


class TestAnswerInline(nested_admin.NestedTabularInline):
    model = TestAnswer
    extra = 0
    ordering = ('question__index',)


class TestAdmin(nested_admin.NestedModelAdmin):
    inlines = [TestAnswerInline]
    list_filter = ['student']


admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Speciality)
admin.site.register(Question, QuestionAdmin)
