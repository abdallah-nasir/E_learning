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
from E_learning.all_email import *
User=get_user_model()

# Create your views here.
AccessKey=os.environ['AccessKey']
Storage_Api=os.environ['Storage_Api']
library_id=os.environ['library_id']
storage_name=os.environ['storage_name']
agartha_cdn=os.environ['agartha_cdn']
BLOGS_FOLDER_COLLECTIONID= os.environ["BLOGS_FOLDER_COLLECTIONID"]
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]


@login_required(login_url="accounts:login")
@check_user_validation  
def add_track(request):
    form=AddAudioBookTrackForm(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            image=request.FILES.get("image")
            instance.user=request.user
            instance.image=None
            data=form.cleaned_data.get("data")
            data={"data":data}
            instance.data=json.dumps(data)
            instance.save()
            headers = {  
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
            url=f"https://storage.bunnycdn.com/{storage_name}/library-audio-book/{instance.slug}/{image}"
            response = requests.put(url,data=image,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    image = f"https://{agartha_cdn}/library-audio-book/{instance.slug}/{image}"
                    instance.image=image
                    instance.save()
            except:
                pass
            messages.success(request,"track added successfully")
            return redirect(reverse("dashboard:audio_book_urls:tracks"))
    context={"form":form}
    return render(request,"audio-book/add_track.html",context)

@login_required(login_url="accounts:login")
@check_user_validation  
def tracks(request):
    if request.user.is_superuser or request.user.is_director:
        tracks=Audio_Book_Tracks.objects.all()
    else:
        tracks=Audio_Book_Tracks.objects.filter(user=request.user)
    paginator = Paginator(tracks, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"tracks":page_obj}
    return render(request,"audio-book/tracks.html",context)


@login_required(login_url="accounts:login")
@check_user_validation  
def single_track(request,slug):
    track=get_object_or_404(Audio_Book_Tracks,slug=slug)
    paginator = Paginator(track.book.all(), 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"track":track,"music":page_obj}
    return render(request,"audio-book/track.html",context)


@login_required(login_url="accounts:login")
@check_user_validation  
def add_audio(request):
    form=AddAudioBookForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            images=request.FILES.getlist("image")
            instance.user=request.user
            instance.save()
            instance.track.book.add(instance)
            instance.track.status="pending"
            instance.track.save()
            messages.success(request,"audio book added successfully")
            return redirect(reverse("dashboard:audio_book_urls:upload_music",kwargs={"slug":instance.slug}))
    context={"form":form}
    return render(request,"audio-book/add_audio.html",context)


@login_required(login_url="accounts:login")
@check_user_validation  
def upload_music(request,slug):
    music=get_object_or_404(Audio_Book,slug=slug)
    form=UploadMusicForm(request.POST or None,request.FILES or None)
    if music.check_music():
        return redirect(reverse("dashboard:audio_book_urls:single_track",kwargs={"slug":music.track.slug}))
    if request.method == "POST":
        if form.is_valid():
            audio=form.cleaned_data.get("music")
            headers = {  
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
            url=f"https://storage.bunnycdn.com/{storage_name}/library-book-music/{music.track.slug}/{music.slug}/{audio}"
            response = requests.put(url,data=audio,headers=headers) 
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    audio_url = f"https://{agartha_cdn}/library-book-music/{music.track.slug}/{music.slug}/{audio}"
                    audio_info=mutagen.File(audio).info
                    music.duration=int(audio_info.length)
                    data={"audio_url":audio_url}
                    music.data=json.dumps(data)
                    music.save()
                    messages.success(request,"music added successfully")
            except:
                pass
    context={"form":form,"music":music}
    return render(request,"audio-book/upload_track_music.html",context)

@login_required(login_url="accounts:login")
@check_user_validation 
def delete_audio(request,slug):
    music=get_object_or_404(Audio_Book,slug=slug)    
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

    return redirect(reverse("dashboard:audio_book_urls:single_track",kwargs={"slug":music.track.slug}))


@login_required(login_url="accounts:login")
@check_user_validation 
def check_audio(request,slug):
    music=get_object_or_404(Audio_Book,slug=slug)    
    if music.check_music() or music.duration:
        return redirect(reverse("dashboard:audio_book_urls:single_track",kwargs={"slug":music.track.slug}))
    else:
        return redirect(reverse("dashboard:audio_book_urls:upload_music",kwargs={"slug":music.slug}))


@login_required(login_url="accounts:login")
@check_user_validation
def track_music(request,slug):
    track=get_object_or_404(Audio_Book_Tracks,slug=slug,status="pending")
    context={"track":track}
    return render(request,"audio-book/track_music.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def edit_audio(request,slug):
    audio=get_object_or_404(Audio_Book_Tracks,user=request.user,slug=slug)
    form =AudioBookEditForm(request.POST or None,instance=audio)
    movie_data=json.loads(audio.data)
    form.initial["data"]=movie_data["data"]
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            data=form.cleaned_data.get("data")
            if data:
                movie_data["data"]=data
            image=form.cleaned_data.get("image")
            if image:
                headers = {
               "Accept": "*/*",
                   "AccessKey": Storage_Api
                        }
                file_url=f"https://storage.bunnycdn.com/{storage_name}/library-audio-book/{instance.slug}/"
                response = requests.get(file_url, headers=headers) 

                data=response.json()
                for i in data:
                    print(data)
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/library-audio-book/{audio.slug}/{i['ObjectName']}"
                    response = requests.delete(image_url,headers=headers)
                    data=response.json()
                    print(data)
                images=request.FILES.getlist("image")
                for i in images:
                    headers = {  
                                "Accept": "*/*", 
                                "AccessKey":Storage_Api}
                    url=f"https://storage.bunnycdn.com/{storage_name}/library-audio-book/{instance.slug}/{i}"
                    response = requests.put(url,data=i,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            image = f"https://{agartha_cdn}/library-audio-book/{instance.slug}/{i}"
                            audio.image=image
                    except:
                        pass
            audio.data=json.dumps(movie_data)
            audio.status="pending"
            form.save()  
            body=f"audio book edit for user {request.user.email}"
            subject="edit audio book"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            # cache.set(f"dashoard_music_email_{request.user}_{instance.id}",True,60*60*3)
            messages.success(request,"audio book edited successfully")
            return redirect(reverse("dashboard:audio_book_urls:tracks"))
    context={"form":form,"audio":audio}
    return render(request,"audio-book/edit_music.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def audio_payment(request): 
    if request.user.is_superuser:
        audios=Library_Payment.objects.filter(library_type=1).order_by("-id")
    else:
        audios=Library_Payment.objects.filter(user=request.user,library_type=1).order_by("-id") 
    paginator = Paginator(audios, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"audio-book/audio_book_payments.html",context)
 
@login_required(login_url="accounts:login")
@check_user_validation
def edit_audio_book_payment(request,slug,id):
    payment=get_object_or_404(Library_Payment,id=id,status="declined")
    track=get_object_or_404(Audio_Book_Tracks,slug=slug)
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            if Library_Payment.objects.filter(user=request.user,library_type=1,content_id=track.id,status="approved").select_related("user").exists():
                messages.success(request,"you already have a payment for this movie")
                return redirect(reverse("accounts:audio_book_payment"))
            form=MusicPaymentForm(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/audio-book-payment/{track.slug}/{payment.user.username}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/audio-book-payment/{audio_book.track.slug}/{payment.user.username}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:audio_book_payment"))
        else:  
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:audio_book_payment"))
    context={"form":form}
    return render(request,"edit_audio_book_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def is_play_music(request,slug):
    music=get_object_or_404(Audio_Book,slug=slug,user=request.user)
    if music.is_play:
        music.is_play = False
    else:
        music.is_play=True
    music.save()
    messages.success(request,"music is play")
    return redirect(reverse("dashboard:audio_book_urls:single_track",kwargs={"slug":music.track.slug}))


@login_required(login_url="accounts:login")
@check_user_validation
@check_audio_book_refund
def audio_book_refund(request,slug,id):   
    payment=get_object_or_404(Library_Payment,id=id,library_type=1)
    refund=Refunds.objects.create(type="audio_book_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","Book":payment.get_audio_book().name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    body=f"a new refund from user {request.user.email}"
    subject="new refund"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    messages.success(request,"Your Refund is Being Review By Admin")
    return redirect(reverse("dashboard:audio_book_urls:audio_payment"))





