from django.core.exceptions import PermissionDenied
from .models import *
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404

from django.contrib import messages
def check_user_is_has_consul(function):
    def wrap(request, *args, **kwargs):
        teacher=get_object_or_404(Teacher_Time,id=kwargs["teacher"],available=True)
        payment = Cosultant_Payment.objects.filter(user=request.user,teacher=teacher).exclude(status="approved")
        consultant=Consultant.objects.filter(user=request.user,teacher=teacher).exclude(status="completed")
        if payment.exists() or consultant.exists():
            messages.error(request,f"You Already Have {consultant.first().status} Consultant")
            return redirect(reverse("accounts:consultant_payment"))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def complete_user_data(function):
    def wrap(request, *args, **kwargs):
        if request.user.first_name == None or request.user.last_name == None or request.user.phone ==None:
            messages.error(request,"complete your information first")
            return redirect(reverse("accounts:account_info"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_teacher_dates(function):
    def wrap(request, *args, **kwargs):
        teacher=get_object_or_404(Teacher_Time,user__slug=kwargs["slug"],available=True)
        consultant = Consultant.objects.filter(teacher=teacher).exclude(status="completed")
        if consultant.exists():
            messages.error(request,f"Teacher {teacher.user.first_name} is not available now")
            return redirect(reverse("consultant:home"))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_teacher_dates_teacher(function):
    def wrap(request, *args, **kwargs):
        teacher=get_object_or_404(Teacher_Time,id=kwargs["teacher"],available=True)
        consultant = Consultant.objects.filter(teacher=teacher).exclude(status="completed")
        if consultant.exists():
            messages.error(request,f"Teacher {teacher.user.first_name} is not available now")
            return redirect(reverse("consultant:home"))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap