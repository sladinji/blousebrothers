# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Conference


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
    model = Conference
    fields = ['title', 'abstract', 'type', 'items', 'specialities']

    # send the user back to their own page after a successful update
    def get_redirect_url(self):
        return reverse('confs:detail',
                       kwargs={'slug': self.request.conf.slug})


class ConferenceListView(LoginRequiredMixin, ListView):
    model = Conference
    # These next two lines tell the view to index lookups by conf
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ConferenceCreateView(LoginRequiredMixin, CreateView):
    model = Conference
    fields = ['title', 'abstract', 'type', 'items', 'specialities', 'questions']
    success_url='.'

    def form_valid(self, form):
        conf = form.save(commit=False)
        conf.owner = self.request.user
        return super().form_valid(form)
