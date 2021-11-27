from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from home.models import Course
from django.shortcuts import get_object_or_404

def check_course_status(function):
    def wrap(request, *args, **kwargs):
        course =get_object_or_404(Course,slug=kwargs["slug"])
        if course.approved != True:
            messages.error(request,"course isn't ready yet")
            return redirect(reverse("home:courses"))
        else:
            return function(request, *args, **kwargs)


    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
