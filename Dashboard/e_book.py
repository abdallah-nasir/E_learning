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
def add_e_book(request):
    form=AddEBookTrackForm(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            image=request.FILES.get("image")
            instance.user=request.user
            instance.image=None
            language=form.cleaned_data.get("language")
            author=form.cleaned_data.get("author")
            publisher=form.cleaned_data.get("publisher")
            isbn=form.cleaned_data.get("isbn")
            about=form.cleaned_data.get("about")
            translator=form.cleaned_data.get("translator")
            book_data={"about":about,"language":language,"author":author,"publisher":publisher,
            "translator":translator,"isbn":isbn}
            instance.data=book_data
            headers = {  
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
            url=f"https://storage.bunnycdn.com/{storage_name}/library-e-book/{instance.slug}/{image}" 
                #upload books
            response = requests.put(url,data=image,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    image = f"https://{agartha_cdn}/library-e-book/{instance.slug}/{image}"
                    instance.image=image
                    instance.save()
            except:
                pass         
            instance.save()
            messages.success(request,"track added successfully")
            return redirect(reverse("dashboard:e_book:upload_pdf",kwargs={"slug":instance.slug}))
    context={"form":form}
    return render(request,"e-book/add_track.html",context)
 
@login_required(login_url="accounts:login")
@check_user_validation  
def books(request):
    if request.user.is_superuser or request.user.is_director:
        tracks=E_Book.objects.all().order_by("-id")
    else:
        tracks=E_Book.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(tracks, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"tracks":page_obj}
    return render(request,"e-book/tracks.html",context)




@login_required(login_url="accounts:login")
@check_user_validation  
def upload_pdf(request,slug):
    book=get_object_or_404(E_Book,slug=slug)
    form=UploadPdf(request.POST or None,request.FILES or None)
    # if book.check_book():
    #     return redirect(reverse("dashboard:e_book:books"))
    if request.method == "POST":
        if form.is_valid():
            pdf=form.cleaned_data.get("pdf")
            book.pdf = pdf
            book.save()
            messages.success(request,"Pdf added successfully")
    
    context={"form":form,"book":book}
    return render(request,"e-book/upload_pdf.html",context)

@login_required(login_url="accounts:login")
@check_user_validation 
def delete_book(request,slug):
    music=get_object_or_404(E_Book,slug=slug)    
    music_url=music.get_book()
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
def check_pdf(request,slug):
    music=get_object_or_404(Audio_Book,slug=slug)    
    if music.check_music() or music.duration:
        return redirect(reverse("dashboard:audio_book_urls:single_track",kwargs={"slug":music.track.slug}))
    else:
        return redirect(reverse("dashboard:audio_book_urls:upload_music",kwargs={"slug":music.slug}))



@login_required(login_url="accounts:login")
@check_user_validation
def edit_book(request,slug):
    book=get_object_or_404(E_Book,user=request.user,slug=slug)
    form =EditEBookTrackForm(request.POST or None,instance=book)
    movie_data=book.data
    form.initial["about"]=movie_data["about"]
    form.initial["language"]=movie_data["language"]
    form.initial["author"]=movie_data["author"]
    form.initial["translator"]=movie_data["translator"]
    form.initial["image"]=None

    form.initial["publisher"]=movie_data["publisher"]
    form.initial["isbn"]=movie_data["isbn"]
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            image=form.cleaned_data.get("image")
            about=form.cleaned_data.get("about")
            language=form.cleaned_data.get("language")
            author=form.cleaned_data.get("author")
            publisher=form.cleaned_data.get("publisher")
            isbn=form.cleaned_data.get("isbn")
            translator=form.cleaned_data.get("translator")

            if image:
                headers = {
               "Accept": "*/*",
                   "AccessKey": Storage_Api
                        }
                file_url=f"https://storage.bunnycdn.com/{storage_name}/library-e-book/{instance.slug}/"
                response = requests.get(file_url, headers=headers) 

                data=response.json()
                for i in data:
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/library-e-book/{book.slug}/{i['ObjectName']}"
                    response = requests.delete(image_url,headers=headers)
                    data=response.json()
                images=request.FILES.getlist("image")
                for i in images:
                    headers = {  
                                "Accept": "*/*", 
                                "AccessKey":Storage_Api}
                    url=f"https://storage.bunnycdn.com/{storage_name}/library-e-book/{instance.slug}/{i}"
                    response = requests.put(url,data=i,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            image = f"https://{agartha_cdn}/library-e-book/{instance.slug}/{i}"
                            book.image=image
                    except:
                        pass
            book_data={"about":about,"language":language,"author":author,"translator":translator,"publisher":publisher,"isbn":isbn}
            book.data=movie_data
            book.status="pending"
            book.save()  
            body=f"audio book edit for user {request.user.email}"
            subject="edit e-book"
            
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            # cache.set(f"dashoard_music_email_{request.user}_{instance.id}",True,60*60*3)
            messages.success(request,"e book edited successfully")
            return redirect(reverse("dashboard:e_book:upload_pdf",kwargs={"slug":instance.slug}))
    context={"form":form,"book":book}
    return render(request,"e-book/edit_book.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def book_payment(request): 
    if request.user.is_superuser:
        audios=Library_Payment.objects.filter(library_type=4).order_by("-id")
    else:
        audios=Library_Payment.objects.filter(user=request.user,library_type=4).order_by("-id") 
    paginator = Paginator(audios, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"e-book/e_book_payments.html",context)
 
@login_required(login_url="accounts:login")
@check_user_validation
def edit_e_book_payment(request,slug,id):
    payment=get_object_or_404(Library_Payment,id=id,status="declined")
    track=get_object_or_404(E_Book,slug=slug)
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            if Library_Payment.objects.filter(user=request.user,library_type=4,content_id=track.id,status="approved").select_related("user").exists():
                messages.success(request,"you already have a payment for this movie")
                return redirect(reverse("accounts:e_book_payment"))
            form=MusicPaymentForm(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/e-book-payment/{track.slug}/{payment.user.username}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/e-book-payment/{track.slug}/{payment.user.username}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("dashboard:e_book_payment"))
    context={"form":form}
    return render(request,"e-book/edit_e_book_payment.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
@check_audio_book_refund
def e_book_refund(request,slug,id):   
    payment=get_object_or_404(Library_Payment,id=id,library_type=4)
    refund=Refunds.objects.create(type="e_book_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","Book":payment.get_e_book().name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    body=f"a new refund from user {request.user.email}"
    subject="new refund"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    messages.success(request,"Your Refund is Being Review By Admin")
    return redirect(reverse("dashboard:audio_book_urls:audio_payment"))

