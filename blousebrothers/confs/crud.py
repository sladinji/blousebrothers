import logging

from django.views.generic import FormView
from django.http import JsonResponse

from djng.views.crud import NgCRUDView

from blousebrothers.auth import (
    ConferenceWritePermissionMixin,
    StudentConferencePermissionMixin,
    ConfRelatedObjPermissionMixin,
    StudentConfRelatedObjPermissionMixin,
    TestPermissionMixin,
)
from .templatetags.bbtricks import is_good_css
from .models import (
    Conference,
    Question,
    Answer,
    AnswerImage,
    ConferenceImage,
    QuestionImage,
    QuestionExplainationImage,
    Test,
    TestAnswer,
    PredictionValidation,
)

logger = logging.getLogger(__name__)


class ConferenceCRUDView(ConferenceWritePermissionMixin, NgCRUDView):
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
        object_data = super().serialize_queryset(queryset)
        ti = object_data['time_taken']
        if ti:
            object_data['time_taken'] = ti.hour * 3600 + ti.minute * 60 + ti.second
        else:
            object_data['time_taken'] = 0
        return object_data


class TestAnswerCRUDView(StudentConfRelatedObjPermissionMixin, NgCRUDView):
    model = TestAnswer

    def get_queryset(self):
        if 'question' in self.request.GET:
            question = Question.objects.get(pk=self.request.GET['question'])
            test = Test.objects.get(student=self.request.user, conf=question.conf)
            return self.model.objects.get(
                question_id=self.request.GET['question'],
                test_id=test.id,
            )


class PredictionValidationCRUDView(NgCRUDView):
    model = PredictionValidation

    def get_queryset(self):
        question = Question.objects.get(pk=self.request.GET['question_id'])
        if question.prediction.first():
            prediction, created = PredictionValidation.objects.get_or_create(
                prediction=question.prediction.first(),
                user=self.request.user
            )
            return prediction
        #  Must return a model object to avoid exception
        return PredictionValidation()


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
        for obj in object_data:
            obj["answered"] = bool(test.answers.get(question_id=obj["pk"]).given_answers)
        if test.finished:
            for obj in object_data:
                obj["score"] = test.answers.get(question_id=obj["pk"]).point
                obj["nb_errors"] = test.answers.get(question_id=obj["pk"]).nb_errors
                obj["nb_fatals"] = test.answers.get(question_id=obj["pk"]).fatals.count()
        return object_data


class BaseQuestionImageCRUDView(NgCRUDView):
    model = QuestionImage

    def get_conf_from_obj(self, obj):
        return obj.question.conf

    def get_queryset(self):
        if 'question_id' in self.request.GET:
            return self.model.objects.filter(
                question_id=self.request.GET['question_id']
            ).order_by('index', 'date_created')


class QuestionImageCRUDView(BaseQuestionImageCRUDView, ConfRelatedObjPermissionMixin):
    """
    CRUD view with conferencier access
    """


class StudentQuestionImageCRUDView(BaseQuestionImageCRUDView, StudentConfRelatedObjPermissionMixin):
    """
    CRUD view with conferencier access
    """
    allowed_methods = ['GET']


class BaseQuestionExplainationImageCRUDView(BaseQuestionImageCRUDView):
    model = QuestionExplainationImage

    def get_conf_from_obj(self, obj):
        return obj.question.conf


class QuestionImageExplainationCRUDView(BaseQuestionExplainationImageCRUDView, ConfRelatedObjPermissionMixin):
    """What else ?"""


class StudentQuestionExplainationImageCRUDView(BaseQuestionExplainationImageCRUDView,
                                               StudentConfRelatedObjPermissionMixin):
    allowed_methods = ['GET']


class BaseAnswerCRUDView(NgCRUDView):
    model = Answer

    def get_conf_from_obj(self, obj):
        return obj.question.conf

    def get_queryset(self):
        if 'question' in self.request.GET:
            return self.model.objects.filter(question_id=self.request.GET['question']).order_by("index")


class AnswerCRUDView(BaseAnswerCRUDView, ConfRelatedObjPermissionMixin):
    """
    Crud view for conferencier access
    """


class StudentAnswerCRUDView(BaseAnswerCRUDView, StudentConfRelatedObjPermissionMixin):
    """
    Crud view for student access
    """
    allowed_methods = ['GET']

    def serialize_queryset(self, queryset):
        """
        Prepare answers for student :
            * add user anwser if test finished to display correction
            * set them with given answers if they exist to display what was answered
            * or turn them all false if not answered yet
        """
        object_data = super().serialize_queryset(queryset)
        question = Question.objects.get(pk=self.request.GET['question'])
        test = Test.objects.get(conf=question.conf, student=self.request.user)
        test_answer = test.answers.get(test=test, question=question)
        if test.finished:
            for obj in object_data:
                obj["user_answer_css"] = is_good_css(Answer.objects.get(id=obj['pk']), test_answer)
                obj["user_answer"] = str(obj['index']) in test_answer.given_answers
        elif test_answer.given_answers:
            for obj in object_data:
                obj["correct"] = str(obj['index']) in test_answer.given_answers
        else:
            for obj in object_data:
                obj["correct"] = False
        return object_data


class BaseAnswerImageCRUDView(NgCRUDView):
    model = AnswerImage

    def get_conf_from_obj(self, obj):
        return obj.question.conf

    def get_queryset(self):
        if 'answer_id' in self.request.GET:
            return self.model.objects.filter(
                answer_id=self.request.GET['answer_id']
            ).order_by('index', 'date_created')


class AnswerImageCRUDView(BaseAnswerImageCRUDView, ConfRelatedObjPermissionMixin):
    """
    CRUD view with conferencier access
    """


class StudentAnswerImageCRUDView(BaseAnswerImageCRUDView, StudentConfRelatedObjPermissionMixin):
    """
    Crud view for conferencier access
    """
    allowed_methods = ['GET']


class BaseUploadImage(ConfRelatedObjPermissionMixin, FormView):
    """
    Base class for image upload (for conf, question, answer)
    """
    kwarg_id = ''
    """FK id name in request of related object"""
    fk_name = ''
    """fk name in model"""
    image_class = None
    """Class used to store image object"""

    def post(self, request, **kwargs):
        fk_id = kwargs[self.kwarg_id]
        obj = self.image_class(**{self.fk_name: fk_id})
        obj.image = request.FILES['file']
        obj.index = self.image_class.objects.filter(**{self.fk_name: fk_id}).count()
        obj.save()
        return JsonResponse({'url': obj.image.url})


class UploadQuestionImage(BaseUploadImage):
    kwarg_id = 'question_id'
    fk_name = kwarg_id
    image_class = QuestionImage


class UploadQuestionExplainationImage(BaseUploadImage):
    kwarg_id = 'question_id'
    fk_name = kwarg_id
    image_class = QuestionExplainationImage


class UploadConferenceImage(BaseUploadImage):
    kwarg_id = 'conference_id'
    fk_name = 'conf_id'
    image_class = ConferenceImage


class UploadAnswerImage(BaseUploadImage):
    kwarg_id = 'answer_id'
    fk_name = kwarg_id
    image_class = AnswerImage
