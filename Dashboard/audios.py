from django.shortcuts import render,redirect
import os
from django.template.defaultfilters import urlencode
from django.urls import reverse  
from Consultant.models import Cosultant_Payment,Consultant,Teacher_Time ,Category as Consultant_Category
from home.models import Course,Payment,Events,Videos,News,Videos
from Blogs.models import (Blog,Blog_Payment,Blog_Images,Prices)
from Blogs.models import Category as Blog_Category
from django.utils import translation
from Quiz.models import *   
from Frontend.models import *
from accounts.models import TeacherForms
from django.core.paginator import Paginator
from .forms import *
from django.core.mail import send_mail,EmailMessage,send_mass_mail,get_connection
from django.db.models import Q
from django.conf import settings
from accounts.forms import ChangeUserDataForm,ChangeTeacherDataForm
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from library.models import *
from .models import *
from django.core.cache import cache 
from django.contrib.auth.decorators import user_passes_test
import json,requests,mutagen
import datetime as today_datetime
from os.path import splitext
from datetime import datetime
from django.contrib.auth import get_user_model
User=get_user_model()
DASHBOARD_EMAIL_HOST = os.environ['DASHBOARD_EMAIL_HOST']
DASHBOARD_EMAIL_USERNAME = os.environ['DASHBOARD_EMAIL_USERNAME']
DASHBOARD_EMAIL_PASSWORD = os.environ['DASHBOARD_EMAIL_PASSWORD']
DASHBOARD_EMAIL_PORT = os.environ['DASHBOARD_EMAIL_PORT']
DASHBOARD_MAIL_CONNECTION = get_connection(
host= DASHBOARD_EMAIL_HOST, 
port=DASHBOARD_EMAIL_PORT, 
username=DASHBOARD_EMAIL_USERNAME, 
password=DASHBOARD_EMAIL_PASSWORD, 
use_tls=False
)  
PAYMENT_EMAIL_USERNAME = os.environ['PAYMENT_EMAIL_USERNAME']
PAYMENT_EMAIL_PASSWORD = os.environ['PAYMENT_EMAIL_PASSWORD']
PAYMENT_EMAIL_PORT = os.environ['PAYMENT_EMAIL_PORT']
PAYMENT_MAIL_CONNECTION = get_connection(
host= DASHBOARD_EMAIL_HOST, 
port=PAYMENT_EMAIL_PORT, 
username=PAYMENT_EMAIL_USERNAME, 
password=PAYMENT_EMAIL_PASSWORD, 
use_tls=False
) 
SUPPORT_EMAIL_HOST = os.environ['SUPPORT_EMAIL_HOST']
SUPPORT_EMAIL_USERNAME = os.environ['SUPPORT_EMAIL_USERNAME']
SUPPORT_EMAIL_PASSWORD = os.environ['SUPPORT_EMAIL_PASSWORD']
SUPPORT_EMAIL_PORT = os.environ['SUPPORT_EMAIL_PORT']
SUPPORT_MAIL_CONNECTION = get_connection(
host= SUPPORT_EMAIL_HOST, 
port=SUPPORT_EMAIL_PORT, 
username=SUPPORT_EMAIL_USERNAME, 
password=SUPPORT_EMAIL_PASSWORD, 
use_tls=False
) 
TASK_NOTIFICATION_EMAIL_USERNAME=os.environ['TASK_NOTIFICATION_EMAIL_USERNAME']
TASK_NOTIFICATION_EMAIL_PASSWORD=os.environ['TASK_NOTIFICATION_EMAIL_PASSWORD']
TASK_NOTIFICATION_EMAIL_HOST=os.environ["TASK_NOTIFICATION_EMAIL_HOST"]
TASK_NOTIFICATION_EMAIL_PORT=os.environ["TASK_NOTIFICATION_EMAIL_PORT"]
TASK_NOTIFICATION_EMAIL_CONNECTION=get_connection(
host= TASK_NOTIFICATION_EMAIL_HOST, 
port=TASK_NOTIFICATION_EMAIL_PORT, 
username=TASK_NOTIFICATION_EMAIL_USERNAME, 
password=TASK_NOTIFICATION_EMAIL_PASSWORD, 
use_tls=False
)
# Create your views here.
AccessKey=os.environ['AccessKey']
Storage_Api=os.environ['Storage_Api']
library_id=os.environ['library_id']
storage_name=os.environ['storage_name']
agartha_cdn=os.environ['agartha_cdn']
BLOGS_FOLDER_COLLECTIONID= os.environ["BLOGS_FOLDER_COLLECTIONID"]
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]

def send_mail_approve(request,user,body,subject):
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=TASK_NOTIFICATION_EMAIL_USERNAME,
        to=[TASK_NOTIFICATION_EMAIL_USERNAME],
        reply_to=[user],
        connection=TASK_NOTIFICATION_EMAIL_CONNECTION
        )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    return True 




@login_required(login_url="accounts:login")
@check_user_validation  
def add_track(request):
    form=AddTrackForm(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            image=request.FILES.get("image")
            instance.user=request.user
            data=instance.cleaned_data.get("data")
            data={"data":data}
            instance.data=json.dumps(data)
            instance.save()
            headers = {  
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
            url=f"https://storage.bunnycdn.com/{storage_name}/library-audio/{instance.slug}/{image}"
            response = requests.put(url,data=image,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    image = f"https://{agartha_cdn}/library-audio/{instance.slug}/{image}"
                    instance.image=image
                    instance.save()
            except:
                pass
            messages.success(request,"track added successfully")
    context={"form":form}
    return render(request,"audio/add_track.html",context)

@login_required(login_url="accounts:login")
@check_user_validation  
def tracks(request):
    if request.user.is_superuser or request.user.is_director:
        tracks=Audio_Tracks.objects.all()
    else:
        tracks=Audio_Tracks.objects.filter(user=request.user)
    paginator = Paginator(tracks, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"tracks":page_obj}
    return render(request,"audio/tracks.html",context)


@login_required(login_url="accounts:login")
@check_user_validation  
def single_track(request,slug):
    track=get_object_or_404(Audio_Tracks,slug=slug)
    paginator = Paginator(track.music.all(), 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"track":track,"music":page_obj}
    return render(request,"audio/track.html",context)


@login_required(login_url="accounts:login")
@check_user_validation  
def add_audio(request):
    form=MusicForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            images=request.FILES.getlist("image")
            instance.user=request.user
            instance.save()
            instance.track.music.add(instance)
            instance.track.status="pending"
            instance.track.save()
            messages.success(request,"audio added successfully")
            return redirect(reverse("dashboard:audios:upload_music",kwargs={"slug":instance.slug}))
    context={"form":form}
    return render(request,"audio/add_audio.html",context)


@login_required(login_url="accounts:login")
@check_user_validation  
def upload_music(request,slug):
    music=get_object_or_404(Music,slug=slug)
    form=UploadMusicForm(request.POST or None,request.FILES or None)
    if music.check_music():
        return redirect(reverse("dashboard:audios:single_track",kwargs={"slug":music.track.slug}))
    if request.method == "POST":
        if form.is_valid():
            audio=form.cleaned_data.get("music")
            headers = {  
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
            url=f"https://storage.bunnycdn.com/{storage_name}/library-music/{music.slug}/{audio}"
            response = requests.put(url,data=audio,headers=headers) 
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    audio_url = f"https://{agartha_cdn}/library-music/{music.slug}/{audio}"
                    audio_info=mutagen.File(audio).info
                    music.duration=int(audio_info.length)
                    data={"audio_url":audio_url}
                    music.data=json.dumps(data)
                    music.save()
                    messages.success(request,"music added successfully")
            except:
                pass
    context={"form":form,"music":music}
    return render(request,"audio/upload_track_music.html",context)

@login_required(login_url="accounts:login")
@check_user_validation 
def delete_audio(request,slug):
    music=get_object_or_404(Music,slug=slug)    
    music_url=music.get_music()
    try:
        music_url_replace=music_url.replace(f"https://{agartha_cdn}",f"https://storage.bunnycdn.com/{storage_name}")
        headers = {
            "AccessKey": Storage_Api,
            "Content-Type": "application/octet-stream",
        }   
        response = requests.delete(music_url_replace,headers=headers)
        data=response.json()
    except: 
        music.delete()

    return redirect(reverse("dashboard:audios:single_track",kwargs={"slug":music.track.slug}))


@login_required(login_url="accounts:login")
@check_user_validation 
def check_audio(request,slug):
    music=get_object_or_404(Music,slug=slug)    
    if music.check_music() or music.duration:
        return redirect(reverse("dashboard:audios:single_track",kwargs={"slug":music.track.slug}))
    else:
        return redirect(reverse("dashboard:audios:upload_music",kwargs={"slug":music.slug}))


@login_required(login_url="accounts:login")
@check_user_validation
def audio_payment(request):
    audios=Library_Payment.objects.filter(user=request.user,library_type=2).order_by("-id")
    paginator = Paginator(audios, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dsahboard/audio/account_audio_payment.html",context)
