from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from home.models import Events
from Consultant.models import  Consultant
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
import datetime

def check_user_validation(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_director:
            return function(request, *args, **kwargs)
        elif request.user.account_type == 'teacher' and request.user.is_active == True:
            return function(request, *args, **kwargs)
        else:
            messages.error(request,"You Don't Have Permission To Login to DashBoard")
            return redirect(reverse("home:home"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def check_if_user_director(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_director:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("dashboard:home"))
        elif request.user.is_superuser or request.user.account_type == "teacher" and request.user.is_active == True:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_event_status(function):
    def wrap(request, *args, **kwargs):
        if request.user.vip == True:
            today= datetime.date.today()
            event=get_object_or_404(Events,id=kwargs["id"])
            if event.end_time <= today:
                event.expired=True
                event.save()
                messages.error(request,"Event Has Expired")
                return redirect(reverse("dashboard:events"))
            else:
                return function(request, *args, **kwargs)
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def admin_director_check(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_director:
            return function(request, *args, **kwargs)
        else:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("dashboard:events"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_teacher_have_consultants(function):
    def wrap(request, *args, **kwargs):
        consult=Consultant.objects.filter(user=request.user,status="approved")
        if consult:
            messages.error(request,"You Should Complete Previous Sessions First")
            return redirect(reverse("dashboard:consultants"))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
