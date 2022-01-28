from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from home.models import Course
from django.shortcuts import get_object_or_404

def check_course_status(function):
    def wrap(request, *args, **kwargs):
        course =get_object_or_404(Course,slug=kwargs["slug"])
        if request.user not in course.students.all():
            messages.error(request,"you should buy course first")
            return redirect(reverse("home:course",kwargs={"slug":course.slug}))
        if course.status != "approved":
            messages.error(request,"course isn't ready yet")
            return redirect(reverse("home:courses"))
        elif course.course_status == "on process":
            messages.error(request,"course is on progress")
            return redirect(reverse("home:course",kwargs={"slug":course.slug}))
        elif course.quiz == None:
            messages.error(request,"course is on progress")
            return redirect(reverse("home:course",kwargs={"slug":course.slug}))
        elif course.quiz:
            if course.quiz.questions == None:
                messages.error(request,"course is on progress")
                return redirect(reverse("home:course",kwargs={"slug":course.slug}))
            else:
                return function(request, *args, **kwargs)
        else:
            return function(request, *args, **kwargs)


    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
