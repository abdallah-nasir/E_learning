from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Course,Payment
from Dashboard.models import Rejects
from django.db.models.query_utils import Q
import datetime
from django.shortcuts import get_object_or_404
def check_if_user_in_course(function):
    def wrap(request, *args, **kwargs):
        course =get_object_or_404(Course,slug=kwargs["course"])
        today=  datetime.date.today()
        if course.students.filter(username=request.user.username).prefetch_related("students").exists():
            last_payment=Payment.objects.filter(user=request.user,expired=False,course=course,status="approved").last()
            if last_payment.expired_at <= today:  
                last_payment.expired=True
                course.students.remove(last_payment.user)
                try:
                    for i in course.videos.all():
                        i.watched_users.remove(last_payment.user)
                        i.save()
                except:
                    pass
                course.save()
                last_payment.save()
                messages.error(request,"payment has been expired for this course")
                return redirect(reverse("accounts:course_payment"))
            else:
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
        if Payment.objects.filter(user=request.user,course=course,status="pending",expired=False).exists():
            messages.error(request,"you already have a pending payment")
            return redirect(reverse("accounts:course_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_user_in_pending_payment_western(function):
    def wrap(request, *args, **kwargs):
        course =get_object_or_404(Course,slug=kwargs["course"])
        if Payment.objects.filter(user=request.user,course=course,expired=False,method="Western Union").exists():
            messages.error(request,"you already have a pending payment")
            return redirect(reverse("accounts:course_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_user_in_pending_payment_bank(function):
    def wrap(request, *args, **kwargs):
        course =get_object_or_404(Course,slug=kwargs["course"])
        if Payment.objects.filter(user=request.user,course=course,expired=False,method="bank").exists():
            messages.error(request,"you already have a pending payment")
            return redirect(reverse("accounts:course_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_user_data_complete(function):
    def wrap(request, *args, **kwargs):
        if not request.user.first_name or not request.user.last_name or not request.user.phone:
            messages.error(request,"please complete your information")
            return redirect(reverse("accounts:account_info"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def check_if_user_in_course_videos(function):
    def wrap(request, *args, **kwargs):
        course=get_object_or_404(Course,slug=kwargs["course"])
        if course.students.filter(username=request.user).exists():
            return function(request, *args, **kwargs)
        else:
            messages.error(request,"you should buy course first")
            return redirect(reverse("home:course",kwargs={"slug":course.slug}))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_payment_has_expired(function):
    def wrap(request, *args, **kwargs):
        course=get_object_or_404(Course,slug=kwargs["course"])
        if course.students.filter(username=request.user).exists():
            today= datetime.date.today()
            payment=Payment.objects.filter(user=request.user,course=course).last()
            # payment.expired_at=today
            # payment.save()
            if payment.expired == True:
                messages.error(request,"payment has been expired for this course")
                return redirect(reverse("accounts:course_payment"))
            elif payment.expired_at <= today:
                if payment.expired == False:
                    payment.expired = True
                    course.students.remove(payment.user)
                    try:
                        for i in course.videos.all():
                            i.watched_users.remove(payment.user)
                            i.save()
                    except:
                        pass
                    course.save()
                    payment.save()
                messages.error(request,"payment has been expired for this course")
                return redirect(reverse("accounts:course_payment"))
            else:
                return function(request, *args, **kwargs)
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

