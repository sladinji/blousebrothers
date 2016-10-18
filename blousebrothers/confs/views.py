# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
import re

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from djng.views.crud import NgCRUDView
from djng.views.mixins import JSONResponseMixin, allow_remote_invocation
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    CreateView,
    FormView,
)

from blousebrothers.shortcuts.auth import BBConferencierReqMixin
from blousebrothers.shortcuts.tools import analyse_conf
from .models import (
    Conference,
    Question,
    Answer,
    ConferenceImage,
    QuestionImage,
    Item,
)
from .forms import ConferenceForm, ConferenceFinalForm



class ConferenceDetailView(BBConferencierReqMixin, DetailView):
    model = Conference
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ConferenceRedirectView(BBConferencierReqMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})


class ConferenceUpdateView(BBConferencierReqMixin, JSONResponseMixin, UpdateView):
    template_name = 'confs/conference_update.html'
    form_class = ConferenceForm
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    # send the user back to their own page after a successful update
    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})

    def get_object(self, queryset=None):
        obj = Conference.objects.get(slug=self.kwargs['slug'])
        return obj

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = self.request.user
            self.object.save()
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
        if formset.is_valid():
            formset.save()
            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

    @allow_remote_invocation
    def sync_data(self, edit_data):
        # process in_data
        conf, question, answers, images, qimages = edit_data
        conf.pop('items')
        conf.pop('specialities')
        conf_pk = conf.pop('pk')
        Conference.objects.filter(pk=conf_pk).update(**conf)
        Question.objects.filter(pk=question.pop('pk')).update(**question)
        for answer in answers:
            Answer.objects.filter(pk=answer.pop('pk')).update(**answer)
        for image in images:
            ConferenceImage.objects.filter(pk=image.pop('pk')).update(**image)
        for image in qimages:
            QuestionImage.objects.filter(pk=image.pop('pk')).update(**image)
        return analyse_conf(Conference.objects.get(pk=conf_pk))

    @allow_remote_invocation
    def delete_anwser_explaination_image(self, data):
        ans = Answer.objects.get(pk=data['pk'])
        ans.explaination_image.delete()
        ans.save()

    @allow_remote_invocation
    def get_keywords(self, data):
        cf = Conference.objects.get(pk=data['pk'])
        txt = cf.get_all_txt()
        ret = []
        for item in Item.objects.all():
            for kw in item.kwords.all():
                if re.search(r'[^\w]'+kw.value+r'[^\w]', txt):
                    ret.append("{} => {}".format(kw.value, item.name))
                    break
        return ret



class ConferenceListView(BBConferencierReqMixin, ListView):
    model = Conference
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user).all()


class ConferenceCreateView(BBConferencierReqMixin, CreateView, FormView):
    template_name = 'confs/conference_form.html'
    form_class = ConferenceForm

    # send the user back to their own page after a successful update
    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})

    def get_success_url(self):
        return reverse('confs:update',
                       kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = self.request.user
            self.object.save()
            # create questions
            for i in range(15):
                q = Question.objects.create(conf=self.object, index=i)
                for j in range(5):
                    Answer.objects.create(question=q, index=j)
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ConferenceFinalView(BBConferencierReqMixin, UpdateView):
    template_name = 'confs/conference_final.html'
    form_class = ConferenceFinalForm
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    model=Conference

    def get_success_url(self):
        return reverse('confs:list')

    def get_context_data(self, **kwargs):
        items = []
        if self.object.items.count() == 0:
            self.object.set_suggested_items()
        else:
            txt = self.object.get_all_txt()
            for item in Item.objects.exclude(
                id__in = self.object.items.all()
            ).all():
                for kw in item.kwords.all():
                    if re.search(r'[^\w]'+kw.value+r'[^\w]', txt):
                        items.append(item)
                        break
        context = super().get_context_data(**{'items':items})

        return context

class ConferenceEditView(BBConferencierReqMixin, UpdateView):
    template_name = 'confs/conference_form.html'
    form_class = ConferenceForm
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    model=Conference

    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})

class ConferenceCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = Conference

class ConferenceImageCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = ConferenceImage

    def get_queryset(self):
        if 'conf' in self.request.GET :
            return self.model.objects.filter(
                conf_id=self.request.GET['conf']
            ).order_by('index', 'date_created')

class QuestionCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = Question

    def get_queryset(self):
        if 'conf' in self.request.GET :
            return self.model.objects.filter(
                conf_id=self.request.GET['conf']).order_by('index')


class QuestionImageCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = QuestionImage

    def get_queryset(self):
        if 'question_id' in self.request.GET :
            return self.model.objects.filter(
                question_id=self.request.GET['question_id']
            ).order_by('index', 'date_created')


class AnswerCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = Answer

    def get_queryset(self):
        if 'question' in self.request.GET:
            return self.model.objects.filter(question_id=self.request.GET['question']).order_by("index")


class HandleConferencierRequest(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        if 'Iwanabe' in request.GET:
            request.user.wanabe_conferencier = True
            request.user.wanabe_conferencier_date = datetime.now()
            request.user.save()
        return render(request, 'confs/wanabe_conferencier.html')


class UploadQuestionImage(BBConferencierReqMixin, TemplateView):

    def post(self, request, **kwargs):
        question_id = kwargs['question_id']
        qimg = QuestionImage(question_id=question_id)
        qimg.image = request.FILES['file']
        qimg.save()
        data = {"url": qimg.image.url}
        return JsonResponse(data)


class UploadConferenceImage(BBConferencierReqMixin, TemplateView):

    def post(self, request, **kwargs):
        conference_id = kwargs['conference_id']
        cimg = ConferenceImage(conf_id=conference_id)
        cimg.image = request.FILES['file']
        cimg.save()
        data = {"url": cimg.image.url}
        return JsonResponse(data)


class UploadAnswerImage(BBConferencierReqMixin, TemplateView):

    def post(self, request, **kwargs):
        answer = Answer.objects.get(pk=kwargs['answer_id'])
        answer.explaination_image = request.FILES['file']
        answer.save()
        data = {"url": answer.explaination_image.url}
        return JsonResponse(data)

