# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from django.shortcuts import redirect

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Conference
from .forms import ConferenceForm, QuestionFormSet


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
    template_name = 'confs/conference_form.html'
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = QuestionFormSet(instance=self.object)
        return context


class ConferenceListView(LoginRequiredMixin, ListView):
    model = Conference
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ConferenceCreateView(LoginRequiredMixin, CreateView):
    template_name = 'confs/conference_form.html'
    form_class = ConferenceForm

    # send the user back to their own page after a successful update
    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})

    def get_context_data(self, **kwargs):
        context = super(ConferenceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = QuestionFormSet(self.request.POST)
        else:
            context['formset'] = QuestionFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = self.request.user
            self.object.save()
            formset.instance = self.object
            for form in formset.ordered_forms:
                form.instance.order = form.cleaned_data['ORDER']
            formset.save()
            #return super().form_valid(form)
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))

