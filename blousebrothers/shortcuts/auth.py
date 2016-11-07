from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

from blousebrothers.confs.models import Conference, Question, Answer


class BBRequirementMixin(LoginRequiredMixin):
    """
    User has to give some info to access.
    """

    def get(self, request, *args, **kwargs):
        if not request.user.gave_all_required_info():
            return redirect("users:update")
        else:
            return super().get(request, *args, **kwargs)


class BBConferencierReqMixin(LoginRequiredMixin):
    """
    User has to be a conferencier to access.
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return super().get(request, *args, **kwargs)
        if not user.gave_all_required_info():
            return redirect("users:update")
        if not user.is_conferencier:
            return redirect("confs:wanabe_conferencier")
        else:
            return super().get(request, *args, **kwargs)


class ConferencePermissionMixin(PermissionRequiredMixin, UserPassesTestMixin):
    permission_required = ['confs.add_conference']

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        return self.object.owner == self.request.user

    def handle_no_permission(self):
        raise PermissionDenied


class ConfRelatedObjPermissionMixin(PermissionRequiredMixin, UserPassesTestMixin):
    permission_required = ['confs.add_conference']

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()(**kwargs)
        if not user_test_result:
            return self.handle_no_permission()
        return super(UserPassesTestMixin, self).dispatch(request, *args, **kwargs)

    def test_func(self, **kwargs):
        if self.request.user.is_superuser:
            return True
        if not kwargs :
            kwargs = self.request.GET
        if 'conf' in kwargs:
            conf = Conference.objects.get(id=kwargs['conf'])
        if 'conference_id' in kwargs:
            conf = Conference.objects.get(id=kwargs['conference_id'])
        elif 'question_id' in kwargs:
            conf = Question.objects.get(id=kwargs['question_id']).conf
        elif 'question' in kwargs:
            conf = Question.objects.get(id=kwargs['question']).conf
        if 'answer_id' in kwargs:
            conf = Answer.objects.get(id=kwargs['answer_id']).question.conf
        return conf.owner == self.request.user
