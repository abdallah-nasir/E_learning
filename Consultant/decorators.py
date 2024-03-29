from django.core.exceptions import PermissionDenied
from .models import *
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404

from django.contrib import messages
def check_user_is_has_consul(function):
    def wrap(request, *args, **kwargs):
        my_teacher=get_object_or_404(Teacher_Time,id=kwargs["teacher"],available=True) 
        payment = Cosultant_Payment.objects.filter(user=request.user,teacher=my_teacher,expired=False,status="pending")
        consultant=Consultant.objects.filter(user=request.user,teacher=my_teacher).exclude(Q(status="completed") | Q(status="refund") |Q(status="declined"))
        if payment.exists():
            messages.error(request,f"You Already Have Pending Consultant payment")
            return redirect(reverse("accounts:consultant_payment"))
        elif consultant.exists():
            messages.error(request,f"You Already Have Pending Consultant")
            return redirect(reverse("accounts:consultants"))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__ 
    return wrap
  
def check_user_is_has_consul_checkout(function):
    def wrap(request, *args, **kwargs):
        my_teacher=get_object_or_404(Teacher_Time,user__slug=kwargs["slug"],available=True) 
        payment = Cosultant_Payment.objects.filter(user=request.user,teacher=my_teacher,expired=False,status="pending")
        consultant=Consultant.objects.filter(user=request.user,teacher=my_teacher).exclude(Q(status="completed") | Q(status="refund") |Q(status="declined"))
        if payment.exists():
            messages.error(request,f"You Already Have Pending Consultant payment")
            return redirect(reverse("accounts:consultant_payment"))
        elif consultant.exists():
            messages.error(request,f"You Already Have Pending Consultant")
            return redirect(reverse("accounts:consultants"))
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__ 
    return wrap

def validate_checkout(function):
    def wrap(request, *args, **kwargs):
        try:
            id=request.GET["consultant"]
            date=request.GET["date"] 
            teacher=get_object_or_404(Teacher_Time,id=id,user__slug=kwargs["slug"])
            if date in teacher.check_teacher_day(): 
                return function(request, *args, **kwargs)
            else:
                messages.error(request,"invalid date")
                return redirect(reverse("consultant:home"))
        except:
            messages.error(request,"invalid date")
            return redirect(reverse("consultant:home"))
    wrap.__doc__ = function.__doc__
    wrap.__name__
    return wrap
def validate_post_checkout(function):
    def wrap(request, *args, **kwargs):
        try:
            id=request.POST["consultant"]
            if Cosultant_Payment.objects.filter(user=request.user,teacher_id=id,expired=False,status="pending").exists():
                messages.error(request,"you already have a pending consultant payment")
                return redirect(reverse("accounts:consultant_payment"))
            date=request.POST["date"]
            teacher=get_object_or_404(Teacher_Time,id=id)
            if date in teacher.check_teacher_day(): 
                return function(request, *args, **kwargs) 
            else:
                messages.error(request,"invalid date")
                return redirect(reverse("consultant:home"))
        except:
            messages.error(request,"invalid date")
            return redirect(reverse("consultant:home"))
    wrap.__doc__ = function.__doc__
    wrap.__name__
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


def check_user_data_form(function):
    def wrap(request, *args, **kwargs):
        user = get_object_or_404(UserDataForm,user=request.user,teacher_id=kwargs["teacher"],accomplished=False)
        if user:
            return function(request, *args, **kwargs)
        else:
            messages.error(request,"complete payment form first")
            return redirect(reverse("consultant:home"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def check_user_is_has_western(function):
    def wrap(request, *args, **kwargs):
        if Cosultant_Payment.objects.filter(user=request.user,teacher_id=kwargs["teacher"],expired=False,method="Western Union").select_related("user").exists():
            messages.error(request,"you already have a pending consultant payment")
            return redirect(reverse("accounts:consultant_payment"))
        else: 
            return function(request, *args, **kwargs) 
  
    wrap.__doc__ = function.__doc__
    wrap.__name__
    return wrap

def check_user_is_has_bank(function):
    def wrap(request, *args, **kwargs):
        if Cosultant_Payment.objects.filter(user=request.user,teacher_id=kwargs["teacher"],expired=False,method="bank").select_related("user").exists():
            messages.error(request,"you already have a pending consultant payment")
            return redirect(reverse("accounts:consultant_payment"))
        else: 
            return function(request, *args, **kwargs) 
  
    wrap.__doc__ = function.__doc__
    wrap.__name__
    return wrap