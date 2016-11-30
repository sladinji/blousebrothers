# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
import time
import re
import logging

from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.core.mail import mail_admins
from djng.views.mixins import JSONResponseMixin, allow_remote_invocation
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    CreateView,
    FormView,
    DeleteView,
)
from django.contrib.auth.mixins import UserPassesTestMixin

from blousebrothers.shortcuts.auth import (
    BBConferencierReqMixin,
    ConferencePermissionMixin,
    ConfRelatedObjPermissionMixin,
    TestPermissionMixin,
)
from blousebrothers.shortcuts.tools import analyse_conf
from .models import (
    Conference,
    Question,
    Answer,
    ConferenceImage,
    QuestionImage,
    Item,
    Test,
    TestAnswer,
)
from .forms import ConferenceForm, ConferenceFinalForm

logger = logging.getLogger(__name__)

class ConferenceDetailView(ConferencePermissionMixin, BBConferencierReqMixin, DetailView):
    model = Conference
    # These next two lines tell the view to index lookups by conf


class ConferenceDeleteView(ConferencePermissionMixin, BBConferencierReqMixin, DeleteView):
    """
    View displayed to confirm deletion. Object are just flaged as deleted but are not
    removed from db. Need to use admin interface to do so.
    """
    template_name = 'confs/conference_delete.html'
    model = Conference

    def delete(self, request, *args, **kwargs):
        """
        Override delete method to simply update object attribute deleted=True.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.deleted = True
        self.object.save()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('confs:list')


class ConferenceUpdateView( ConferencePermissionMixin, BBConferencierReqMixin, JSONResponseMixin, UpdateView):
    """
    Main Angular JS interface where you can edit question, images...
    """
    template_name = 'confs/conference_update.html'
    form_class = ConferenceForm

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
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.order_by('-edition_progress').all()
        else :
            qry = self.model.objects.filter(owner=self.request.user)
            qry = qry.order_by('edition_progress')
            return qry.all()


class ConferenceCreateView(PermissionRequiredMixin, BBConferencierReqMixin, CreateView, FormView):
    template_name = 'confs/conference_form.html'
    form_class = ConferenceForm
    model = Conference
    permission_required = ['confs.add_conference']

    def handle_no_permission(self):
        return redirect("confs:wanabe_conferencier")

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


class ConferenceFinalView(ConferencePermissionMixin, BBConferencierReqMixin, UpdateView):
    template_name = 'confs/conference_final.html'
    form_class = ConferenceFinalForm
    model = Conference

    def get_success_url(self):
        return reverse('confs:list')

    def get_context_data(self, **kwargs):
        items = []
        if self.object.items.count() == 0:
            self.object.set_suggested_items()
        else:
            txt = self.object.get_all_txt()
            for item in Item.objects.exclude(
                id__in=self.object.items.all()
            ).all():
                for kw in item.kwords.all():
                    if re.search(r'[^\w]'+kw.value+r'[^\w]', txt):
                        items.append(item)
                        break
        context = super().get_context_data(**{'items': items})

        return context


class ConferenceEditView( ConferencePermissionMixin, BBConferencierReqMixin, UpdateView):
    template_name = 'confs/conference_form.html'
    form_class = ConferenceForm
    model = Conference

    def get_redirect_url(self):
        return reverse('confs:update',
                       kwargs={'slug': self.request.conf.slug})

    def get_success_url(self):
        return reverse('confs:update',
                       kwargs={'slug': self.object.slug})


class HandleConferencierRequest(LoginRequiredMixin, TemplateView):
    email_template = '''
Nom : {}
Email : {}
Lien : {}{}{}'''

    def get(self, request, *args, **kwargs):
        if 'Iwanabe' in request.GET:
            request.user.is_conferencier = True
            request.user.wanabe_conferencier = False
            request.user.wanabe_conferencier_date = datetime.now()
            permission = Permission.objects.get(name='Can add conference')
            request.user.user_permissions.add(permission)
            request.user.save()
            msg = self.email_template.format(request.user.name,
                                             request.user.email,
                                             'https://' if request.is_secure() else 'http://',
                                             request.get_host(),
                                             reverse('admin:users_user_change',
                                                     args=(request.user.id,)
                                                     )
                                             )
            logger.info(msg)
            mail_admins('Passage conférencier', msg)

        return render(request, 'confs/wanabe_conferencier.html')


class BuyedConferenceListView(LoginRequiredMixin, ListView):
    model = Test
    # These next two lines tell the view to index lookups by conf
    paginate_by = 10

    def get_queryset(self):
        qry = self.model.objects.filter(student=self.request.user)
        qry = qry.order_by('progress')
        return qry.all()


class TestUpdateView(TestPermissionMixin, JSONResponseMixin, UpdateView):
    """
    Main test view.
    """
    model = Test
    fields = []

    def get_context_data(self, **kwargs):
        """
        Add time_taken var to context for timer initialization. time_taken units is
        milliseconds as angularjs timer needs.
        """
        tt = self.get_object().time_taken
        time_taken = (tt.hour * 3600 + tt.minute * 60 + tt.second) * 1000 if tt else 0
        return super().get_context_data(time_taken=time_taken, **kwargs)

    def get_object(self, queryset=None):
        """
        TestAnswers are created here, when user starts his test.
        """
        conf = Conference.objects.get(slug=self.kwargs['slug'])
        test = Test.objects.get(conf=conf, student=self.request.user)
        if not test.answers.count():
            for question in conf.questions.all():
                TestAnswer.objects.create(question=question, test=test)
        return test

    @allow_remote_invocation
    def send_answers(self, data):
        """
        API to collect test's answers.

        :param data: {'answers': [0..4] => list of checked answers indexes,
                      'millis': time elapsed in milliseconds since test started,
                      }
        """
        answers = data["answers"]
        time_taken = datetime.fromtimestamp(data["millis"]/1000.0).time()
        question = Question.objects.get(pk=answers[0]['question'])
        test = Test.objects.get(conf=question.conf, student=self.request.user)
        ta = TestAnswer.objects.get(test=test, question=question)

        ta.given_answers = ','.join([str(answer['index']) for answer in answers if answer['correct']])
        if test.time_taken :
            last_time = test.time_taken.hour * 3600 + test.time_taken.minute * 60 + test.time_taken.second
            this_time = time_taken.hour * 3600 + time_taken.minute * 60 + time_taken.second
            ta.time_taken = datetime.fromtimestamp(this_time - last_time)
        else:
            ta.time_taken = time_taken
        ta.save()
        test.time_taken = time_taken
        test.save()
