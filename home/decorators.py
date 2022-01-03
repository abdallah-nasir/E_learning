from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Course,Payment
from Dashboard.models import Rejects
from django.shortcuts import get_object_or_404
def check_if_user_in_course(function):
    def wrap(request, *args, **kwargs):

        course =get_object_or_404(Course,slug=kwargs["course"])
        if course.students.filter(username=request.user).exists():
            messages.error(request,"you already have this course")
            return redirect(reverse("home:course",kwargs={"slug":course.slug}))
        else:
            return function(request, *args, **kwargs)


    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_user_in_pending_payment(function):
    def wrap(request, *args, **kwargs):
        course =get_object_or_404(Course,slug=kwargs["course"])
        if Payment.objects.filter(user=request.user,course=course,status="pending").exists():
            messages.error(request,"you already have a pending payment")
            return redirect(reverse("accounts:course_payment"))
        elif Payment.objects.filter(user=request.user,course=course,status="declined"):
            messages.error(request,"Please check you declined payment")
            return redirect(reverse("accounts:course_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_user_data_complete(function):
    def wrap(request, *args, **kwargs):
        if request.user.first_name == None or request.user.last_name == None or request.user.phone == None:
            messages.error(request,"please complete your information")
            return redirect(reverse("account:account_info"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

