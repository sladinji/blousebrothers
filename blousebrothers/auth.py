from datetime import datetime

from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission
from django.utils.decorators import method_decorator
from django.core.mail import mail_admins
from termsandconditions.decorators import terms_required

from blousebrothers.confs.models import Conference, Question, Answer, Test
from blousebrothers.tools import get_full_url


@method_decorator(terms_required, name='dispatch')
class BBLoginRequiredMixin(LoginRequiredMixin):
    login_url = '/accounts/login/'


class BBConferencierReqMixin(BBLoginRequiredMixin, UserPassesTestMixin):
    """
    User has to be a conferencier to access.
    """

    email_template = '''
    -Nom : {}
    -Email : {}
    -Lien : {}'''

    def check_conferencier(self, user):
        if not user.is_conferencier:
            user.is_conferencier = True
            user.wanabe_conferencier = False
            user.wanabe_conferencier_date = datetime.now()
            permission = Permission.objects.get(name='Can add conference')
            user.user_permissions.add(permission)
            user.save()
            msg = self.email_template.format(
                user.name,
                user.email,
                get_full_url(self.request, 'admin:users_user_change', args=(user.id,))
            )
            mail_admins('Passage conférencier', msg)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        if not self.request.user.gave_all_required_info:
            return False
        self.check_conferencier(self.request.user)
        return True

    def handle_no_permission(self):
        messages.warning(self.request,
                         _("Avant de pouvoir publier une conférence, merci de compléter le formulaire ci-dessous. "
                           "Ces informations sont nécessaires pour activer ton compte. "
                           "C'est gratuit et sans engagement")
                         )
        return redirect("users:update")


class TestPermissionMixin(BBLoginRequiredMixin, UserPassesTestMixin):
    """
    Base class to test check student access to a test.
    """

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        return self.object.student == self.request.user


class MangoPermissionMixin(BBLoginRequiredMixin, UserPassesTestMixin):
    """
    Check if user gave all info to deal with mangopay.
    """

    msg_access_denied = _('Merci de compléter le formulaire ci-dessous pour pouvoir créditer ton compte.')

    def test_func(self):
        return self.request.user.gave_all_mangopay_info

    def handle_no_permission(self):
        messages.error(self.request, self.msg_access_denied)
        return redirect('users:update')


class CanAddConfPermission(PermissionRequiredMixin):
    """
    User can create conference.
    """
    permission_required = ['confs.add_conference']


class IsConfOwner(BBConferencierReqMixin):
    """
    User is conf owner, root.
    """
    def test_func(self):
        if not super().test_func():
            return False
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        return self.object.owner == self.request.user


class ConferenceReadPermissionMixin(IsConfOwner):
    """
    Access granted if user is_conferencier or (no add_conference required)
    """


class ConferenceWritePermissionMixin(IsConfOwner):
    """
    Check if user is conference's owner and has add_conference permission
    """


class StudentConferencePermissionMixin(BBLoginRequiredMixin, UserPassesTestMixin):
    """
    Check if student can access conf.
    """

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        return Test.objects.filter(
            student=self.request.user,
            conf=self.get_object(),
        ).count() != 0

    def handle_no_permission(self):
        raise PermissionDenied


class BaseConfRelatedObjPermissionMixin():
    """
    Base classe to get access associated conf objec
    """

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()(**kwargs)
        if not user_test_result:
            return self.handle_no_permission()
        return super(UserPassesTestMixin, self).dispatch(request, *args, **kwargs)

    def get_conf_from_obj(self, obj):
        return obj.conf

    def get_conf(self, **kwargs):
        if not kwargs:
            kwargs = self.request.GET
        if not kwargs:
            kwargs = self.request.POST
        if 'conf' in kwargs:
            conf = Conference.objects.get(id=kwargs['conf'])
        elif 'conference_id' in kwargs:
            conf = Conference.objects.get(id=kwargs['conference_id'])
        elif 'pk' in kwargs:
            obj = self.model.objects.get(id=kwargs['pk'])
            conf = self.get_conf_from_obj(obj)
        elif 'question_id' in kwargs:
            conf = Question.objects.get(id=kwargs['question_id']).conf
        elif 'question' in kwargs:
            conf = Question.objects.get(id=kwargs['question']).conf
        elif 'answer_id' in kwargs:
            conf = Answer.objects.get(id=kwargs['answer_id']).question.conf
        return conf


class ConfRelatedObjPermissionMixin(BaseConfRelatedObjPermissionMixin, PermissionRequiredMixin, UserPassesTestMixin):
    permission_required = ['confs.add_conference']

    def test_func(self, **kwargs):
        if self.request.user.is_superuser:
            return True
        conf = self.get_conf(**kwargs)
        return conf.owner == self.request.user


class StudentConfRelatedObjPermissionMixin(BaseConfRelatedObjPermissionMixin, UserPassesTestMixin):
    """
    Test if a requested object belong to a conference with access granted to user.
    """

    def test_func(self, **kwargs):
        if self.request.user.is_superuser:
            return True
        return Test.objects.filter(
            student=self.request.user,
            conf=self.get_conf(),
        ).count() != 0
