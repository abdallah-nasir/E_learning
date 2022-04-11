from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from library.models import Audio_Tracks, Library_Payment,Movies,Audio_Book_Tracks
from .models import TeacherForms
from django.contrib import messages
from django.contrib.auth import get_user_model
from functools import wraps
from home.models import Course,Payment
from Blogs.models import Blog_Payment
from Dashboard.models import Refunds
from Consultant.models import Consultant,Cosultant_Payment
import datetime
from django.shortcuts import get_object_or_404
User=get_user_model()


 
def check_edit_blog_pyment(function):
    def wrap(request, *args, **kwargs):
        payment=get_object_or_404(Blog_Payment,id=kwargs["id"])
        another_payment=Blog_Payment.objects.filter(user=request.user,type=2,expired=False).exclude(id=payment.id).select_related("user")
        if request.user.vip:
            messages.error(request,"you are already a member")
            return redirect(reverse("accounts:blog_payment"))
        for i in another_payment:
            while i.status == "approved" or i.status == "pending":
                messages.error(request,"you are already have another payment")
                return redirect(reverse("accounts:blog_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
def check_edit_course_pyment(function):
    def wrap(request, *args, **kwargs):
        payment=get_object_or_404(Payment,id=kwargs["id"])
        another_payment=Payment.objects.filter(user=request.user,course=payment.course,expired=False).exclude(id=payment.id).select_related("user")
        for i in another_payment:
            while i.status == "approved" or i.status == "pending":
                messages.error(request,"you are already have another payment")
                return redirect(reverse("accounts:course_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def check_edit_consultant_pyment(function):
    def wrap(request, *args, **kwargs):
        payment=get_object_or_404(Cosultant_Payment,id=kwargs["id"])
        another_payment=Cosultant_Payment.objects.filter(user=request.user,teacher=payment.teacher).exclude(id=payment.id).select_related("user")
        for i in another_payment:
            while i.status == "approved" or i.status == "pending": 
                messages.error(request,"you are already have another payment")
                return redirect(reverse("accounts:consultant_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
def check_user_is_student(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            messages.error(request,"you are already a teacher")
            return redirect(reverse("accounts:account_info"))
        elif request.user.account_type == 'student':
            form=TeacherForms.objects.filter(teacher=request.user)
            if form.exists():
                if form[0].status == "pending":
                    messages.error(request,"your request is being review by admins")
                    return redirect(reverse("accounts:account_info"))
                elif form[0].status == 'approved':
                    messages.success(request,"your request has been approved")
                    return redirect(reverse("dashboard:home"))
                else:
                    return function(request, *args, **kwargs)

            else:
                return function(request, *args, **kwargs)

        else:
            return redirect(reverse("accounts:account_info"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def check_user_is_teacher(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            return redirect(reverse("dashboard:home"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def redirect_teacher_course_payment(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            return redirect(reverse("dashboard:course_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def redirect_teacher_blog_payment(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            return redirect(reverse("dashboard:blog_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def redirect_teacher_consultant_payment(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            return redirect(reverse("dashboard:consultant_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
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
            return redirect(reverse("accounts:course_payment"))
        elif payment.created_at + datetime.timedelta(days=30) <= today : 
            messages.error(request,"you have passed 30 days returns")
            return redirect(reverse("accounts:course_payment"))
        elif refunds.exists():
            messages.error(request,"you already have pending refund for this payment")
            return redirect(reverse("accounts:course_payment"))
        count=course.videos.filter(watched_users__username=request.user).count()
        if count >= 3:
            messages.error(request,"you already watched 2 videos in this course")
            return redirect(reverse("accounts:course_payment"))
        return function(request, *args, **kwargs)
    return wrap

def check_movies_refund(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        movie=get_object_or_404(Movies,slug=kwargs['slug'])
        payment=get_object_or_404(Library_Payment,id=kwargs["id"])
        today= datetime.date.today()
        refunds=Refunds.objects.filter(user=request.user,type="movie_payment",content_id=payment.id).exclude(status="approved")
        if payment.status == 'refund':
            messages.error(request,"this payment is already refunded")
            return redirect(reverse("accounts:movies_payment"))
        elif payment.created_at + datetime.timedelta(days=30) <= today : 
            messages.error(request,"you have passed 30 days returns")
            return redirect(reverse("accounts:movies_payment"))
        elif refunds.exists():
            messages.error(request,"you already have pending refund for this payment")
            return redirect(reverse("accounts:movies_payment"))
        return function(request, *args, **kwargs)
    return wrap

def check_music_refund(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Tracks,slug=kwargs['slug'])
        payment=get_object_or_404(Library_Payment,id=kwargs["id"])
        today= datetime.date.today()
        refunds=Refunds.objects.filter(user=request.user,type="music_payment",content_id=payment.id).exclude(status="approved")
        if payment.status == 'refund':
            messages.error(request,"this payment is already refunded")
            return redirect(reverse("accounts:audio_payment"))
        elif payment.created_at + datetime.timedelta(days=30) <= today : 
            messages.error(request,"you have passed 30 days returns")
            return redirect(reverse("accounts:audio_payment"))
        elif refunds.exists():
            messages.error(request,"you already have pending refund for this payment")
            return redirect(reverse("accounts:audio_payment"))
        return function(request, *args, **kwargs)
    return wrap

def check_consultant_refund(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        payment=get_object_or_404(Cosultant_Payment,id=kwargs["id"])
        refunds=Refunds.objects.filter(user=request.user,type="consultant_payment",content_id=payment.id).exclude(status="approved")
        today= datetime.date.today()
        if payment.status == 'refund':
            messages.error(request,"this payment is already refunded")
            return redirect(reverse("accounts:consultant_payment"))
        elif payment.status == "completed":
            messages.error(request,"payment already completed")
            return redirect(reverse("accounts:consultant_payment"))
        elif refunds.exists():
            messages.error(request,"you already have pending refund for this payment")
            return redirect(reverse("accounts:consultant_payment"))
        elif payment.consultant:
            if payment.consultant.date < today or payment.consultant.date == today:
                messages.error(request,"time already passed")
                return redirect(reverse("accounts:consultant_payment"))
            elif payment.consultant.status == "completed" or payment.consultant.status == "started":
                messages.error(request,"consultant already completed")
                return redirect(reverse("accounts:consultant_payment"))
            elif payment.consultant.date > today:
                difference= payment.consultant.date - today
                if difference.days < 3:
                    print("here")
                    messages.error(request,"time already passed")
                    return redirect(reverse("accounts:consultant_payment"))
                else:
                    return function(request, *args, **kwargs)
        else:
            return function(request, *args, **kwargs)
    return wrap


def redirect_teacher_movies_payment(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            return redirect(reverse("dashboard:movies_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def redirect_teacher_audio_payment(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            return redirect(reverse("dashboard:audios:audio_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



def redirect_audio_book_payment(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            return redirect(reverse("dashboard:audio_book_urls:audio_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_audio_book_refund(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Book_Tracks,slug=kwargs['slug'])
        payment=get_object_or_404(Library_Payment,id=kwargs["id"])
        if payment.method == "Western Union":
            messages.error(request,"You cant refund Western Union Payment")
            return redirect(reverse("dashboard:audio_book_urls:audio_payment"))
        today= datetime.date.today() 
        refunds=Refunds.objects.filter(user=request.user,type="audio_book_payment",content_id=payment.id).exclude(status="approved")
        if payment.status == 'refund':
            messages.error(request,"this payment is already refunded")
            return redirect(reverse("dashboard:audio_book_urls:audio_payment"))
        elif payment.created_at + datetime.timedelta(days=30) <= today : 
            messages.error(request,"you have passed 30 days returns")
            return redirect(reverse("dashboard:audio_book_urls:audio_payment"))
        elif refunds.exists():
            messages.error(request,"you already have pending refund for this payment")
            return redirect(reverse("dashboard:audio_book_urls:audio_payment"))
        else:
            return function(request, *args, **kwargs)
    return wrap
  