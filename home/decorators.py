from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Course,Payment
from django.shortcuts import get_object_or_404
def check_if_user_in_course(function):
    def wrap(request, *args, **kwargs):

        course =get_object_or_404(Course,slug=kwargs["course"])
        if request.user in course.students.all():
            messages.error(request,"sorry you should buy course first")
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
            return redirect(reverse("home:course",kwargs={"slug":course.slug}))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
