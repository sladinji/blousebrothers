from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class BBRequirementMixin(LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        if not request.user.gave_all_required_info() :
            return redirect("users:update")
        else :
            return super().get(request, *args, **kwargs)

