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
    form=AddTrackForm(request.POST or None,request.FILES or None)
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
            return redirect(reverse("dashboard:audios:tracks"))
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
            url=f"https://storage.bunnycdn.com/{storage_name}/library-music/{music.track.slug}/{music.slug}/{audio}"
            response = requests.put(url,data=audio,headers=headers) 
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    audio_url = f"https://{agartha_cdn}/library-music/{music.track.slug}/{music.slug}/{audio}"
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
def track_music(request,slug):
    track=get_object_or_404(Audio_Tracks,slug=slug,status="pending")
    context={"track":track}
    return render(request,"audio/track_music.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def edit_audio(request,slug):
    audio=get_object_or_404(Audio_Tracks,user=request.user,slug=slug)
    form =MusicLibraryEditForm(request.POST or None,instance=audio)
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
                file_url=f"https://storage.bunnycdn.com/{storage_name}/library-audio/{instance.slug}/"
                response = requests.get(file_url, headers=headers) 

                data=response.json()
                for i in data:
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/library-audio/{audio.slug}/{i['ObjectName']}"
                    response = requests.delete(image_url,headers=headers)
                    data=response.json()
                images=request.FILES.getlist("image")
                for i in images:
                    headers = {  
                                "Accept": "*/*", 
                                "AccessKey":Storage_Api}
                    url=f"https://storage.bunnycdn.com/{storage_name}/library-audio/{instance.slug}/{i}"
                    response = requests.put(url,data=i,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            image = f"https://{agartha_cdn}/library-audio/{instance.slug}/{i}"
                            audio.image=image
                    except:
                        pass
            audio.data=json.dumps(movie_data)
            audio.status="pending"
            form.save()  
            time=cache.get(f"dashoard_music_email_{request.user}_{instance.id}")
            if time and time == True:
                pass
            else:
                body=f"movie edit for user {request.user.email}"
                subject="edit movie"
                send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                cache.set(f"dashoard_music_email_{request.user}_{instance.id}",True,60*60*3)
            messages.success(request,"music edited successfully")
            return redirect(reverse("dashboard:audios:tracks"))
    context={"form":form,"audio":audio}
    return render(request,"audio/edit_music.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def audio_payment(request):
    if request.user.is_superuser:
        audios=Library_Payment.objects.filter(library_type=2).order_by("-id")
    else:
        audios=Library_Payment.objects.filter(user=request.user,library_type=2).order_by("-id")
    paginator = Paginator(audios, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"audio/audio_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
@check_edit_audio_pyment
def edit_music_payment(request,slug,id):
    track=get_object_or_404(Audio_Tracks,slug=slug)
    payment=get_object_or_404(Library_Payment,library_type=2,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            form=MusicPaymentForm(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/music-payment/{track.slug}/{payment.user.username}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/music-payment/{track.slug}/{payment.user.username}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:audio_payment"))
        else:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:audio_payment"))
    context={"form":form}
    return render(request,"audio/edit_audio_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def is_play_music(request,slug):
    music=get_object_or_404(Music,slug=slug,user=request.user)
    if music.is_play:
        music.is_play = False
    else:
        music.is_play=True
    music.save()
    messages.success(request,"music is play")
    return redirect(reverse("dashboard:audios:single_track",kwargs={"slug":music.track.slug}))


@login_required(login_url="accounts:login")
@check_user_validation
@check_music_refund
def music_refund(request,slug,id):   
    payment=get_object_or_404(Library_Payment,id=id,library_type=2)
    refund=Refunds.objects.create(type="music_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","music":payment.get_music().name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    body=f"a new refund from user {request.user.email}"
    subject="new refund"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    messages.success(request,"Your Refund is Being Review By Admin")
    return redirect(reverse("dashboard:audios:audio_payment"))

@login_required(login_url="accounts:login")
@for_admin_only  
def accpet_paymob_music_payment_refund(request,payment,refund):
    url_1 = "https://accept.paymob.com/api/auth/tokens"
    data_1 = {"api_key": PAYMOB_API_KEY}
    r_1 = requests.post(url_1, json=data_1)
    token = r_1.json().get("token")
    body={
            "auth_token": token,
            "transaction_id": payment.transaction_number,
            "amount_cents": payment.amount * 100
            }
    url = "https://accept.paymob.com/api/acceptance/void_refund/refund"
    r_1=requests.post(url=url,json=body)
    try:
        r_2=r_1.json()
        if r_2["success"] == True:
            payment.status ="refund"
            payment.save()
            refund.status="approved"
            refund.save()
            send_mail(
                'Payment Refunded',
                "Successfull Payment Refund",
                PAYMENT_EMAIL_USERNAME,
                [payment.user.email],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
            messages.success(request,"Payment Refunded")
        else:
            messages.error(request,"invalid payment refund")
    except:
        messages.error(request,"invalid payment refund")



@login_required(login_url="accounts:login")
@for_admin_only  
def paymob_music_payment_refund(request,payment):
    url_1 = "https://accept.paymob.com/api/auth/tokens"
    data_1 = {"api_key": PAYMOB_API_KEY}
    r_1 = requests.post(url_1, json=data_1)
    token = r_1.json().get("token")
    body={
            "auth_token": token,
            "transaction_id": payment.transaction_number,
            "amount_cents": payment.amount * 100
            }
    url = "https://accept.paymob.com/api/acceptance/void_refund/refund"
    r_1=requests.post(url=url,json=body)
    try:
        r_2=r_1.json()
        if r_2["success"] == True:
            payment.status ="refund"
            try:
                payment.get_movies().buyers.remove(payment.user)
                payment.get_movies().save()
            except:
                pass
            payment.save()
            refund=Refunds.objects.create(type="music_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,status="approved")
            my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","music":payment.get_music().name}]}
            refund.data=json.dumps(my_data)
            refund.save()
            messages.success(request,"Payment Refunded")
        else:
            messages.error(request,"invalid payment refund")
    except:
        messages.error(request,"invalid payment refund")


login_required(login_url="accounts:login")
@for_admin_only  
def artist_add(request):
    form = AddArtistForm(request.POST or None)
    user=None
    if request.method == "POST":
        if form.is_valid():
            username=form.cleaned_data.get("user")
            user=User.objects.filter(username=username)
            if user.exists():
                Artist.objects.create(user=user.last(),status="approved")
                messages.success(request,"artist added successfully")
    context={"form":form,"user":user}
    return render(request,"audio/add_artist.html",context)
