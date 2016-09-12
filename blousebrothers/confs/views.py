# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from djng.views.crud import NgCRUDView
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    CreateView,
    TemplateView,
)

from blousebrothers.shortcuts.auth import BBConferencierReqMixin
from blousebrothers.shortcuts.tools import analyse_conf
from .models import Conference, Question, Answer, ConferenceImage
from .forms import ConferenceForm
from djng.views.mixins import JSONResponseMixin, allow_remote_invocation



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


class ConferenceUpdateView(BBConferencierReqMixin,JSONResponseMixin, UpdateView):
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
        conf, question, answers = edit_data
        conf.pop('items')
        conf.pop('specialities')
        conf_pk = conf.pop('pk')
        Conference.objects.filter(pk=conf_pk).update(**conf)
        Question.objects.filter(pk=question.pop('pk')).update(**question)
        for answer in answers:
            Answer.objects.filter(pk=answer.pop('pk')).update(**answer)
        return analyse_conf(Conference.objects.get(pk=conf_pk))


class ConferenceListView(BBConferencierReqMixin, ListView):
    model = Conference
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user).all()


class ConferenceCreateView(BBConferencierReqMixin, CreateView):
    template_name = 'confs/conference_form.html'
    form_class = ConferenceForm

    # send the user back to their own page after a successful update
    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})

    def form_valid(self, form):
        #context = self.get_context_data()
        #formset = context['formset']
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = self.request.user
            self.object.save()
            for i, image in enumerate(form.cleaned_data['images']):
                ConferenceImage.objects.create(image=image, index=i, conf=self.object)
            # create questions
            for i in range(15):
                q = Question.objects.create(conf=self.object, index=i)
                for j in range(5):
                    Answer.objects.create(question=q, index=j)
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))




class ConferenceCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = Conference

class ConferenceImageCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = ConferenceImage

    def get_queryset(self):
        if 'conf' in self.request.GET :
            return self.model.objects.filter(conf_id=self.request.GET['conf']).order_by('index')

class QuestionCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = Question

    def get_queryset(self):
        if 'conf' in self.request.GET :
            return self.model.objects.filter(conf_id=self.request.GET['conf']).order_by('index')


class AnswerCRUDView(BBConferencierReqMixin, NgCRUDView):
    model = Answer

    def get_queryset(self):
        if 'question' in self.request.GET :
            return self.model.objects.filter(question_id=self.request.GET['question']).order_by("index")


class HandleConferencierRequest(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        if 'Iwanabe' in request.GET :
            request.user.wanabe_conferencier = True
            request.user.wanabe_conferencier_date = datetime.now()
            request.user.save()
        return render(request, 'confs/wanabe_conferencier.html')

