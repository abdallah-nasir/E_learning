from .models import *
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
import datetime
from Blogs.models import check_if_payment_expired
from django.db.models.query_utils import Q



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
def check_if_in_can_watch_movie(function):
    def wrap(request, *args, **kwargs):
        movie=get_object_or_404(Movies,slug=kwargs['slug'],status="approved")
        if request.user.is_kemet_vip == False:
            messages.error(request,"you should subscribe first")
            return redirect(reverse("blogs:pricing"))
        else:
            if check_if_payment_expired(user=request.user) == False:
                if movie.get_price() > 0: 
                    payment=Library_Payment.objects.filter(user=request.user,library_type=3,status="approved").select_related("user")
                    if payment.exists():        
                        return function(request, *args, **kwargs)
                    else:
                        messages.error(request,"You Should Buy Movie First")
                        return redirect(reverse("library:movie_payment",kwargs={"slug":movie.slug}))
                else:
                    return function(request, *args, **kwargs)
            else:
                return redirect(reverse("blogs:pricing"))


    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def movies_check_payment(function):
    def wrap(request, *args, **kwargs):
        payment=Library_Payment.objects.filter(user=request.user,library_type=3).exclude(Q(status="refund") | Q(status="declined")).select_related("user").last()
        if payment:
            if payment.status == "approved":
                return function(request, *args, **kwargs)
            else:
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:movies_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_if_there_payment(function):
    def wrap(request, *args, **kwargs):
        payment=Library_Payment.objects.filter(user=request.user,library_type=3).exclude(status="refund").select_related("user").last()
        if payment:
            if payment.status == "approved":
                return function(request, *args, **kwargs)
            else:
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:movies_payment"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_audio_payment_page(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Tracks,slug=kwargs["slug"],status="approved")
        if track.buyers.filter(username=request.user.username).exists():
            messages.error(request,"you already have this music")
            return redirect(reverse("accounts:audio_payment"))
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=2,content_id=track.id).exclude(Q(status="refund") | Q(status="declined")).select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:audio_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library:single_track",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 

def check_audio_payment_western(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Tracks,slug=kwargs["slug"],status="approved")
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=2,content_id=track.id,method="Western Union",expired=False).select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:audio_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library:single_track",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 
 
 
def check_video_payment_western(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Movies,slug=kwargs["slug"],status="approved")
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=3,content_id=track.id,method="Western Union",expired=False).select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:movies_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library:single_movie",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 

 
def check_video_payment_bank(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Movies,slug=kwargs["slug"],status="approved")
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=3,content_id=track.id,method="bank",expired=False).select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:movies_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library:single_movie",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 

def check_audio_payment_bank(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Tracks,slug=kwargs["slug"],status="approved")
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=2,content_id=track.id,method="bank",expired=False).select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:audio_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library:single_track",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 
def check_user_is_kemet_vip(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_kemet_vip == False:
            messages.error(request,"you should subscribe first")
            return redirect(reverse("blogs:pricing"))       
        else:
            if check_if_payment_expired(user=request.user) == False:
                return function(request, *args, **kwargs) 
            else:
                return redirect(reverse("blogs:pricing"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 

def check_audio_book_payment_page(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Book_Tracks,slug=kwargs["slug"],status="approved")
        if track.buyers.filter(username=request.user.username).exists():
            messages.error(request,"you already have this music")
            return redirect(reverse("accounts:audio_payment"))
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=1,content_id=track.id,status="pending").select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:audio_book_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library_audio_book:single_track",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 

def check_audio_book_payment_western(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Book_Tracks,slug=kwargs["slug"],status="approved")
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=1,content_id=track.id,method="Western Union",expired=False).select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:audio_book_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library:audio_book:single_track",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 

def check_audio_book_payment_bank(function):
    def wrap(request, *args, **kwargs):
        track=get_object_or_404(Audio_Book_Tracks,slug=kwargs["slug"],status="approved")
        if track.price and track.price > 0:
            payment=Library_Payment.objects.filter(user=request.user,library_type=1,content_id=track.id,method="bank",expired=False).select_related("user")
            if payment.exists():
                messages.error(request,"you already have an existing payment")
                return redirect(reverse("accounts:audio_book_payment"))              
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(request,"track is free")
            return redirect(reverse("library:audio_book:single_track",kwargs={"slug":track.slug}))  
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 
 