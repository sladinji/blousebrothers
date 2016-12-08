import logging
import datetime
import time

from django.views.generic import TemplateView
from django.http import JsonResponse

from djng.views.crud import NgCRUDView

from blousebrothers.shortcuts.auth import (
    ConferencePermissionMixin,
    StudentConferencePermissionMixin,
    ConfRelatedObjPermissionMixin,
    StudentConfRelatedObjPermissionMixin,
    TestPermissionMixin,
)
from .models import (
    Conference,
    Question,
    Answer,
    AnswerImage,
    ConferenceImage,
    QuestionImage,
    Test,
    TestAnswer,
    QuestionComment,
)

logger = logging.getLogger(__name__)


class ConferenceCRUDView(ConferencePermissionMixin, NgCRUDView):
    model = Conference


class StudentConferenceCRUDView(StudentConferencePermissionMixin, NgCRUDView):
    model = Conference
    allowed_methods = ['GET']


class TestCRUDView(TestPermissionMixin, NgCRUDView):
    model = Test

    def get_object(self):
        if 'conf' in self.request.GET:
            return self.model.objects.get(
                student=self.request.user,
                conf_id=self.request.GET['conf']
            )

    def get_queryset(self):
        if 'conf' in self.request.GET:
            return self.model.objects.get(
                student=self.request.user,
                conf_id=self.request.GET['conf']
            )

    def serialize_queryset(self, queryset):
        """
        Set all question to false before returning it
        """
        object_data = super().serialize_queryset(queryset)
        ti = object_data['time_taken']
        if ti :
            object_data['time_taken'] = ti.hour * 3600 + ti.minute * 60 + ti.second
        else :
            object_data['time_taken'] = 0
        return object_data


class TestAnswerCRUDView(StudentConfRelatedObjPermissionMixin, NgCRUDView):
    model = TestAnswer

    def get_object(self):
        if 'question' in self.request.GET:
            question = Question.objects.get(pk=self.request.GET['question'])
            test = Test.objects.get(student=self.request.user, conf=question.conf)
            return self.model.objects.get(
                question_id=self.request.GET['question'],
                test_id=test.id,
            )


class BaseConferenceImageCRUDView(NgCRUDView):
    model = ConferenceImage

    def get_queryset(self):
        if 'conf' in self.request.GET:
            return self.model.objects.filter(
                conf_id=self.request.GET['conf']
            ).order_by('index', 'date_created')


class ConferenceImageCRUDView(ConfRelatedObjPermissionMixin, BaseConferenceImageCRUDView):
    """
    Access for conferencier
    """


class StudentConferenceImageCRUDView(StudentConfRelatedObjPermissionMixin, BaseConferenceImageCRUDView):
    """
    Access for student
    """
    allowed_methods = ['GET']


class BaseQuestionCRUDView(NgCRUDView):
    model = Question

    def get_queryset(self):
        if 'conf' in self.request.GET:
            return self.model.objects.filter(
                conf_id=self.request.GET['conf']).order_by('index')


class QuestionCRUDView(ConfRelatedObjPermissionMixin, BaseQuestionCRUDView):
    """
    CRUD view for conferencier access
    """


class StudentQuestionCRUDView(StudentConfRelatedObjPermissionMixin, BaseQuestionCRUDView):
    """
    CRUD view for student access
    """
    allowed_methods = ['GET']

    def serialize_queryset(self, queryset):
        """
        Set all question to false before returning it
        """
        object_data = super().serialize_queryset(queryset)
        conf = Conference.objects.get(pk=self.request.GET['conf'])
        test = Test.objects.get(conf=conf, student=self.request.user)
        for obj in object_data :
            obj["answered"] = bool(test.answers.get(question_id=obj["pk"]).given_answers)
        return object_data


class BaseQuestionImageCRUDView(NgCRUDView):
    model = QuestionImage

    def get_queryset(self):
        if 'question_id' in self.request.GET:
            return self.model.objects.filter(
                question_id=self.request.GET['question_id']
            ).order_by('index', 'date_created')


class QuestionImageCRUDView(ConfRelatedObjPermissionMixin, BaseQuestionImageCRUDView):
    """
    CRUD view with conferencier access
    """


class StudentQuestionImageCRUDView(StudentConfRelatedObjPermissionMixin, BaseQuestionImageCRUDView):
    """
    CRUD view with conferencier access
    """
    allowed_methods = ['GET']


class BaseAnswerCRUDView(NgCRUDView):
    model = Answer

    def get_queryset(self):
        if 'question' in self.request.GET:
            return self.model.objects.filter(question_id=self.request.GET['question']).order_by("index")


class AnswerCRUDView(ConfRelatedObjPermissionMixin, BaseAnswerCRUDView):
    """
    Crud view for conferencier access
    """


class StudentAnswerCRUDView(StudentConfRelatedObjPermissionMixin, BaseAnswerCRUDView):
    """
    Crud view for conferencier access
    """
    allowed_methods = ['GET']

    def serialize_queryset(self, queryset):
        """
        Prepare answers for student :
            * turn them all false if not answered yet
            * set them with given answers if they exist
        """
        object_data = super().serialize_queryset(queryset)
        question = Question.objects.get(pk=self.request.GET['question'])
        test = Test.objects.get(conf=question.conf, student=self.request.user)
        answer = test.answers.get(test=test, question=question)
        if answer :
            for obj in object_data :
                obj["correct"] = str(obj['index']) in answer.given_answers
        else :
            for obj in object_data:
                obj["correct"] = False
        return object_data


class BaseAnswerImageCRUDView(NgCRUDView):
    model = AnswerImage

    def get_queryset(self):
        if 'answer_id' in self.request.GET:
            return self.model.objects.filter(
                answer_id=self.request.GET['answer_id']
            ).order_by('index', 'date_created')


class AnswerImageCRUDView(ConfRelatedObjPermissionMixin, BaseAnswerImageCRUDView):
    """
    CRUD view with conferencier access
    """


class StudentAnswerImageCRUDView(StudentConfRelatedObjPermissionMixin, BaseAnswerImageCRUDView):
    """
    Crud view for conferencier access
    """
    allowed_methods = ['GET']


class StudentQuestionCommentView(StudentConfRelatedObjPermissionMixin, TemplateView):

    def post(self, request, **kwargs):
        QuestionComment.objects.create(
            question_id=request.POST['question_id'],
            student=request.user,
            comment=request.POST['comment'],
        )
        return JsonResponse(dict(success=1))


class BaseUploadImage(ConfRelatedObjPermissionMixin, TemplateView):
    """
    Base class for image upload (for conf, question, answer)
    """
    kwarg_id = ''
    """Id of related object"""
    image_class = None
    """Class used to store image object"""

    def post(self, request, **kwargs):
        fk_id = kwargs[self.kwarg_id]
        obj = self.image_class(**{self.kwarg_id: fk_id})
        obj.image = request.FILES['file']
        obj.index = self.image_class.objects.filter(**{self.kwarg_id: fk_id}).count()
        obj.save()
        return JsonResponse({'url': obj.image.url})


class UploadQuestionImage(BaseUploadImage):
    kwarg_id = 'question_id'
    image_class = QuestionImage


class UploadConferenceImage(BaseUploadImage):
    kwarg_id = 'conference_id'
    image_class = ConferenceImage


class UploadAnswerImage(BaseUploadImage):
    kwarg_id = 'answer_id'
    image_class = AnswerImage
