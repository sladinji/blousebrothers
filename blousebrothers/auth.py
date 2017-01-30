from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from termsandconditions.decorators import terms_required


from blousebrothers.confs.models import Conference, Question, Answer, Test
from django.utils.decorators import method_decorator



@method_decorator(terms_required, name='dispatch')
class BBLoginRequiredMixin(LoginRequiredMixin):
    login_url = '/accounts/login/'


class BBRequirementMixin(BBLoginRequiredMixin):
    """
    User has to give some info to access.
    """

    def get(self, request, *args, **kwargs):
        if not request.user.gave_all_required_info():
            messages.error(self.request, 'Pour être conférencier, vous devez compléter le formulaire ci-dessous.')
            return redirect("users:update")
        else:
            return super().get(request, *args, **kwargs)


class BBConferencierReqMixin(BBLoginRequiredMixin):
    """
    User has to be a conferencier to access.
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return super().get(request, *args, **kwargs)
        if not user.gave_all_required_info():
            messages.error(self.request, 'Pour être conférencier, vous devez compléter le formulaire ci-dessous.')
            return redirect("users:update")
        if not user.is_conferencier:
            return redirect("confs:wanabe_conferencier")
        else:
            return super().get(request, *args, **kwargs)


class TestPermissionMixin(BBLoginRequiredMixin, UserPassesTestMixin):
    """
    Base class to test check student access to a test.
    """

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        return self.object.student == self.request.user


class PassTestPermissionMixin(TestPermissionMixin):
    """
    Same as TestPermissionMixin but user also need a valid subscription
    """

    def test_func(self):
        if not super().test_func():
            return False
        return self.request.user.has_valid_subscription()

    def handle_no_permission(self):
        messages.error(self.request, _("Tu dois disposer d'un abonnement à jour pour faire une conf"))
        return redirect("users:detail", **{'username':self.request.user.username})


class CanAddConfPermission(PermissionRequiredMixin):
    """
    User can create conference.
    """
    permission_required = ['confs.add_conference']


class IsConfOwner(UserPassesTestMixin):
    """
    User is conf owner, root.
    """
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        return self.object.owner == self.request.user


class ConferenceReadPermissionMixin(BBLoginRequiredMixin, IsConfOwner):
    """
    Access granted if user is_conferencier or (no add_conference required)
    """


class ConferenceWritePermissionMixin(BBLoginRequiredMixin, CanAddConfPermission, IsConfOwner):
    """
    Check if user is conference's owner and has add_conference permission
    """

    def handle_no_permission(self):
        raise PermissionDenied


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
