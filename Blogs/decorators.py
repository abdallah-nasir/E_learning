from django.core.exceptions import PermissionDenied
from .models import Blog
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Blog_Payment,Prices
from django.db.models.query_utils import Q

def check_user_is_member(function):
    def wrap(request, *args, **kwargs):

        blog = Blog.objects.get(slug=kwargs['slug'])
        if blog.paid == True:
            if request.user.vip == True or blog.user == request.user:
                return function(request, *args, **kwargs)
            else:
                messages.error(request,"You Should Be A Member To Access Blogs")
                return redirect(reverse("blogs:pricing"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_user_status(function):
    def wrap(request, *args, **kwargs):
        if request.user.vip == True:
            today= datetime.date.today()
            payment=Blog_Payment.objects.filter(user=request.user,type=1,expired=False,status="approved").last()
            if payment.expired_at <= today:
                payment.expired=True
                payment.save()
                request.user.vip =False
                request.user.save()
                messages.error(request,"your membership has expired")
                return redirect(reverse("blogs:pricing"))
            else:
                messages.error(request,"You Already A Member")
                return redirect(reverse("blogs:blogs"))
        else:
            if Blog_Payment.objects.filter(user=request.user,type=1,expired=False).exclude(Q(status="refund") | Q(status="declined")).select_related("user").exists():
                messages.error(request,"You have a pending request ,our team will review your request")
                return redirect(reverse("accounts:blog_payment"))
            else:
                return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def complete_user_data(function):
    def wrap(request, *args, **kwargs):
        if not request.user.first_name or not request.user.last_name or not request.user.phone:
            messages.error(request,"complete your information first")
            return redirect(reverse("accounts:account_info"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


import datetime
def check_blogs_payment_status(function):
    def wrap(request, *args, **kwargs):
        blog = get_object_or_404(Blog,slug=kwargs["slug"],status="approved")
        if blog.paid == False:
            return function(request, *args, **kwargs)
        if request.user.vip == True:
            today= datetime.date.today()
            payment=Blog_Payment.objects.filter(user=request.user,type=1,expired=False,status="approved").select_related("user").last()
            if payment.expired_at <= today:
                payment.expired=True
                payment.save()
                request.user.vip =False
                request.user.save()
                messages.error(request,"your membership has expired")
                return redirect(reverse("blogs:pricing"))
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"You Should Be A Member To Access Blogs")
            return redirect(reverse("blogs:pricing"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



def check_blogs_payment_western_status(function):
    def wrap(request, *args, **kwargs):
        if Blog_Payment.objects.filter(user=request.user,type=2,method="Western Union",expired=False).select_related("user").exists():
            messages.error(request,"your already have a payment")
            return redirect(reverse("accounts:blog_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_blogs_payment_bank_status(function):
    def wrap(request, *args, **kwargs):
        if Blog_Payment.objects.filter(user=request.user,type=2,method="bank",expired=False).select_related("user").exists():
            messages.error(request,"your already have a payment")
            return redirect(reverse("accounts:blog_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap