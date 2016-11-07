import logging
from datetime import datetime

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.contrib.auth.models import Permission

from djng.views.crud import NgCRUDView

from blousebrothers.shortcuts.auth import (
    BBConferencierReqMixin,
    ConferencePermissionMixin,
    ConfRelatedObjPermissionMixin,
)
from .models import (
    Conference,
    Question,
    Answer,
    ConferenceImage,
    QuestionImage,
)

logger = logging.getLogger(__name__)


class ConferenceCRUDView(ConferencePermissionMixin, BBConferencierReqMixin, NgCRUDView):
    model = Conference


class ConferenceImageCRUDView(ConfRelatedObjPermissionMixin, BBConferencierReqMixin, NgCRUDView):
    model = ConferenceImage

    def get_queryset(self):
        if 'conf' in self.request.GET:
            return self.model.objects.filter(
                conf_id=self.request.GET['conf']
            ).order_by('index', 'date_created')


class QuestionCRUDView(ConfRelatedObjPermissionMixin, BBConferencierReqMixin, NgCRUDView):
    model = Question

    def get_queryset(self):
        if 'conf' in self.request.GET:
            return self.model.objects.filter(
                conf_id=self.request.GET['conf']).order_by('index')


class QuestionImageCRUDView(ConfRelatedObjPermissionMixin, BBConferencierReqMixin, NgCRUDView):
    model = QuestionImage

    def get_queryset(self):
        if 'question_id' in self.request.GET:
            return self.model.objects.filter(
                question_id=self.request.GET['question_id']
            ).order_by('index', 'date_created')


class AnswerCRUDView(ConfRelatedObjPermissionMixin, BBConferencierReqMixin, NgCRUDView):
    model = Answer

    def get_queryset(self):
        if 'question' in self.request.GET:
            return self.model.objects.filter(question_id=self.request.GET['question']).order_by("index")


class UploadQuestionImage(ConfRelatedObjPermissionMixin, BBConferencierReqMixin, TemplateView):

    def post(self, request, **kwargs):
        question_id = kwargs['question_id']
        qimg = QuestionImage(question_id=question_id)
        qimg.image = request.FILES['file']
        qimg.save()
        data = {"url": qimg.image.url}
        return JsonResponse(data)


class UploadConferenceImage(ConfRelatedObjPermissionMixin, BBConferencierReqMixin, TemplateView):

    def post(self, request, **kwargs):
        conference_id = kwargs['conference_id']
        cimg = ConferenceImage(conf_id=conference_id)
        cimg.image = request.FILES['file']
        cimg.save()
        data = {"url": cimg.image.url}
        return JsonResponse(data)


class UploadAnswerImage(ConfRelatedObjPermissionMixin, BBConferencierReqMixin, TemplateView):

    def post(self, request, **kwargs):
        answer = Answer.objects.get(pk=kwargs['answer_id'])
        answer.explaination_image = request.FILES['file']
        answer.save()
        data = {"url": answer.explaination_image.url}
        return JsonResponse(data)
