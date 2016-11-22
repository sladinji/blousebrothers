import logging

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
    ConferenceImage,
    QuestionImage,
    Test,
    TestAnswer,
)

logger = logging.getLogger(__name__)


class ConferenceCRUDView(ConferencePermissionMixin, NgCRUDView):
    model = Conference


class StudentConferenceCRUDView(StudentConferencePermissionMixin, NgCRUDView):
    model = Conference


class TestCRUDView(TestPermissionMixin, NgCRUDView):
    model = Test


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


class ConferenceImageCRUDView(ConfRelatedObjPermissionMixin, NgCRUDView):
    model = ConferenceImage

    def get_queryset(self):
        if 'conf' in self.request.GET:
            return self.model.objects.filter(
                conf_id=self.request.GET['conf']
            ).order_by('index', 'date_created')


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


class QuestionImageCRUDView(ConfRelatedObjPermissionMixin, NgCRUDView):
    model = QuestionImage

    def get_queryset(self):
        if 'question_id' in self.request.GET:
            return self.model.objects.filter(
                question_id=self.request.GET['question_id']
            ).order_by('index', 'date_created')


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


class UploadQuestionImage(ConfRelatedObjPermissionMixin, TemplateView):

    def post(self, request, **kwargs):
        question_id = kwargs['question_id']
        qimg = QuestionImage(question_id=question_id)
        qimg.image = request.FILES['file']
        qimg.save()
        data = {"url": qimg.image.url}
        return JsonResponse(data)


class UploadConferenceImage(ConfRelatedObjPermissionMixin, TemplateView):

    def post(self, request, **kwargs):
        conference_id = kwargs['conference_id']
        cimg = ConferenceImage(conf_id=conference_id)
        cimg.image = request.FILES['file']
        cimg.save()
        data = {"url": cimg.image.url}
        return JsonResponse(data)


class UploadAnswerImage(ConfRelatedObjPermissionMixin, TemplateView):

    def post(self, request, **kwargs):
        answer = Answer.objects.get(pk=kwargs['answer_id'])
        answer.explaination_image = request.FILES['file']
        answer.save()
        data = {"url": answer.explaination_image.url}
        return JsonResponse(data)
