from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class BBRequirementMixin(LoginRequiredMixin):
    """
    User has to give some info to access.
    """

    def get(self, request, *args, **kwargs):
        if not request.user.gave_all_required_info() :
            return redirect("users:update")
        else :
            return super().get(request, *args, **kwargs)

class BBConferencierReqMixin(LoginRequiredMixin):
    """
    User has to be a conferencier to access.
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser :
            return super().get(request, *args, **kwargs)
        if not user.gave_all_required_info() :
            return redirect("users:update")
        if not user.is_conferencier :
            return redirect("confs:wanabe_conferencier")
        else :
            return super().get(request, *args, **kwargs)
