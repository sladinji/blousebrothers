# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from djng.views.crud import NgCRUDView

from .models import Conference, Question, Answer, ConferenceImage
from .forms import ConferenceForm


class ConferenceDetailView(LoginRequiredMixin, DetailView):
    model = Conference
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ConferenceRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})


class ConferenceUpdateView(LoginRequiredMixin, UpdateView):
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


class ConferenceListView(LoginRequiredMixin, ListView):
    model = Conference
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.model.objects.filter(owner = self.request.user).all()


class ConferenceCreateView(LoginRequiredMixin, CreateView):
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
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))




class ConferenceCRUDView(LoginRequiredMixin, NgCRUDView):
    model = Conference

class ConferenceImageCRUDView(LoginRequiredMixin, NgCRUDView):
    model = ConferenceImage

    def get_queryset(self):
        if 'conf' in self.request.GET :
            return self.model.objects.filter(conf_id=self.request.GET['conf']).order_by('index')

class QuestionCRUDView(LoginRequiredMixin, NgCRUDView):
    model = Question

    def get_queryset(self):
        if 'conf' in self.request.GET :
            return self.model.objects.filter(conf_id=self.request.GET['conf']).order_by('index')


class AnswerCRUDView(LoginRequiredMixin, NgCRUDView):
    model = Answer

    def get_queryset(self):
        if 'question' in self.request.GET :
            return self.model.objects.filter(question_id=self.request.GET['question']).order_by("index")
