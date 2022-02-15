from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from .models import Refunds
from home.models import Events,Course,Payment
from Blogs.models import Blog
from Consultant.models import  Cosultant_Payment,Consultant
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
import datetime,json
from functools import wraps

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

def for_admin_only(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("dashboard:home"))

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

def check_if_teacher_has_event(function):
    def wrap(request, *args, **kwargs):
        events=Events.objects.filter(user=request.user,status="start")
        if events.exists():
            messages.error(request,"Finish Previous Event First")
            return redirect(reverse("dashboard:events"))
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



def check_if_teacher_have_pending_video_upload(function):
    def wrap(request, *args, **kwargs):
        course=get_object_or_404(Course,Instructor=request.user,slug=kwargs["slug"])
        if course:
            if course.videos.filter(duration=0).exists():
                messages.error(request,"You Should Upload Previous Videos First")
                return redirect(reverse("dashboard:videos"))
            else:
                return function(request, *args, **kwargs)

        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_blog_video(function):
    def wrap(request, *args, **kwargs):
        blog=get_object_or_404(Blog,slug=kwargs["slug"])
        allowed_type=["video"]
        if blog.blog_type not in allowed_type:
            messages.error(request,"invalid blog type")
            return redirect(reverse("dashboard:blogs"))
        # elif blog.status == "approved":
        #     messages.error(request,"please edit blog first")
        #     return redirect(reverse("dashboard:blogs"))
        elif blog.video and blog.get_blog_video_status == None:
            messages.error(request,"please edit blog first,you already have a video")
            return redirect(reverse("dashboard:blogs"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap  



def check_blog_video_progress(function):
    def wrap(request, *args, **kwargs):
        blog=get_object_or_404(Blog,slug=kwargs["slug"])
        try:
            blog_data=json.loads(blog.data)
            length=blog_data["video_guid"]
            return function(request, *args, **kwargs)
        except:
            blog.delete()
            messages.error(request,"we found some error please re-create your blog")
            return  redirect(reverse("dashboard:blogs"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap  

def check_blog_audio(function):
    def wrap(request, *args, **kwargs):
        blog=get_object_or_404(Blog,slug=kwargs["slug"])
        allowed_type=["audio"]
        if blog.blog_type not in allowed_type:
            messages.error(request,"invalid blog type")
            return redirect(reverse("dashboard:blogs"))
        # elif blog.status == "approved":
        #     messages.error(request,"please edit blog first")
        #     return redirect(reverse("dashboard:blogs"))
        elif blog.video :
            messages.error(request,"please edit blog first,you already have an audio")
            return redirect(reverse("dashboard:blogs"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap  


def check_consultant_refund(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        payment=get_object_or_404(Cosultant_Payment,id=kwargs["id"])
        refunds=Refunds.objects.filter(user=request.user,type="consultant_payment",content_id=payment.id).exclude(status="approved")
        today= datetime.date.today()
        if payment.status == 'refund':
            messages.error(request,"this payment is already refunded")
            return redirect(reverse("dashboard:consultant_payment"))
        elif payment.status == "completed":
            messages.error(request,"payment already completed")
            return redirect(reverse("dashboard:consultant_payment"))
        elif refunds.exists():
            messages.error(request,"you already have pending refund for this payment")
            return redirect(reverse("dashboard:consultant_payment"))
        elif payment.consultant:
            if payment.consultant.date < today or payment.consultant.date == today:
                messages.error(request,"time already passed")
                return redirect(reverse("dashboard:consultant_payment"))
            elif payment.consultant.status == "completed" or payment.consultant.status == "started":
                messages.error(request,"consultant already completed")
                return redirect(reverse("dashboard:consultant_payment"))
            elif payment.consultant.date > today:
                difference= payment.consultant.date - today
                if difference.days < 3:
                    print("here")
                    messages.error(request,"time already passed")
                    return redirect(reverse("dashboard:consultant_payment"))
                else:
                    return function(request, *args, **kwargs)
        else:
            return function(request, *args, **kwargs)
    return wrap


def check_course_refund(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        course=get_object_or_404(Course,slug=kwargs['slug'])
        payment=get_object_or_404(Payment,id=kwargs["id"])
        today= datetime.date.today()
        print(payment.created_at + datetime.timedelta(days=30))
        refunds=Refunds.objects.filter(user=request.user,type="course_payment",content_id=payment.id).exclude(status="approved")
        if payment.status == 'refund':
            messages.error(request,"this payment is already refunded")
            return redirect(reverse("dashboard:course_payment"))
        elif payment.created_at + datetime.timedelta(days=30) <= today : 
            messages.error(request,"you have passed 30 days returns")
            return redirect(reverse("dashboard:course_payment"))
        elif refunds.exists():
            messages.error(request,"you already have pending refund for this payment")
            return redirect(reverse("dashboard:course_payment"))
        count=course.videos.filter(watched_users__username=request.user).count()
        if count >= 3:
            messages.error(request,"you already watched 2 videos in this course")
            return redirect(reverse("dashboard:course_payment"))
        return function(request, *args, **kwargs)
    return wrap
