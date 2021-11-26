from django.core.exceptions import PermissionDenied
from .models import *
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404

from django.contrib import messages
def check_user_is_has_consul(function):
    def wrap(request, *args, **kwargs):
        teacher=get_object_or_404(Teacher_Time,id=kwargs["teacher"])
        consult = Consultant.objects.filter(Q(user=request.user,teacher=teacher,completed=False) | Q(user=request.user,teacher=teacher,pending=True))
        if consult:
            messages.error(request,"You Already Have Pending Consultant")
            return redirect(reverse("home:home"))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap