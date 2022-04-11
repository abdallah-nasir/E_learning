
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
import json,requests
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


def change_cache_value(request,name,data_check,action,number=0,domain=None):
    if domain == None: 
        data=cache.get("data")
    else:
        data=cache.get("kemet_data")
    if data:
        if action == "remove":
            cache_name=data[name]
            if data_check in cache_name:
                print("here")
                cache_name.remove(data_check)
                if domain == None : 
                    cache.set("data",data,60*60*24*3)
                else:
                    cache.set("kemet_data",data,60*60*24*3)
        elif action == "add":
            cache_name=data[name]
            print(len(cache_name))
            if number >= len(cache_name):
                print("here")
                if data_check not in cache_name:
                    cache_name.append(data_check)
                    if  domain == None:
                        cache.set("data",data,60*60*24*3)
                    else:
                        cache.set("kemet_data",data,60*60*24*3)
    return data
def change_blog_cache(request,data_check,action,domain=None):
    if domain == None:
        data=cache.get("blog_data")
    else:
        data=cache.get("kemet_blog_data")
    if data:
        if action == "remove":
            blogs_cache=data["blogs"]
            slider_cache=data["slider"]
            recent_cache=data["recent_blogs"]
            if data_check in blogs_cache:
                blogs_cache.remove(data_check)
            elif data_check in slider_cache:
                slider_cache.remove(data_check)
            elif data_check in recent_cache:
                recent_cache.remove(data_check) 
            if domain == None:
                cache.set("blog_data",data,60*60*24)
            else:
                cache.set("kemet_blog_data",data,60*60*24)
        elif action == "add":
            blogs_cache=data["blogs"]
            slider_cache=data["slider"]
            recent_cache=data["recent_blogs"]
            if data_check not in blogs_cache:
                blogs_cache.append(data_check)
            elif data_check not in slider_cache and len(slider_cache) < 5:
                slider_cache.append(data_check)
            elif data_check not in recent_cache and len(recent_cache) < 6:
                recent_cache.append(data_check)
            if domain == None:
                cache.set("blog_data",data,60*60*24)
            else:
                cache.set("kemet_blog_data",data,60*60*24)
    return data

def delete_image(request,file_url,image_url,headers,name):
    response = requests.get(file_url, headers=headers) 
    data=response.json()
    for i in data:
        print(i['ObjectName'],name)
        while i['ObjectName'] == name: 
            response = requests.delete(image_url,headers=headers)
            data=response.json()
            print(data)
            break
    return data
class FailedJsonResponse(JsonResponse):
    def __init__(self, data):
        super().__init__(data)
        self.status_code = 400

def add_images_to_library(request,form,images,url_name,instance):
    status=False
    instance=form.save(commit=False)
    library_data=json.loads(instance.data) 
    library_data["images"]=[]
    instance.save() 
    for i in images:
        headers = {  
                    "Accept": "*/*", 
                    "AccessKey":Storage_Api}
        url=f"https://storage.bunnycdn.com/{storage_name}/{url_name}/{instance.slug}/{i}"
        response = requests.put(url,data=i,headers=headers)
        data=response.json()
        try:
            if data["HttpCode"] == 201:
                image = f"https://{agartha_cdn}/{url_name}/{instance.slug}/{i}"
                library_data["images"].append(image)
        except:
            pass
    instance.data=json.dumps(library_data)
    print(instance.data)
    instance.save()
    messages.success(request,"library added successfully")
    status=True
    return status

def add_movies_to_library(request,slug,instance):
    url = f"http://video.bunnycdn.com/library/{library_id}/collections"
    data_1 = {"name":slug}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/*+json",
        "AccessKey": AccessKey
    }
    response = requests.post( url, json=data_1, headers=headers)
    reponse_data=response.json()
    instance.save()
    url = f"http://video.bunnycdn.com/library/{library_id}/videos"         
    data_2 = {"title":slug,"collectionId":reponse_data["guid"]}
    response = requests.post( url, json=data_2, headers=headers)
    data_3=response.json()
    movies_data=json.loads(instance.data)
    movies_data["video_uid"]=data_3["guid"]
    movies_data["collection_guid"]=reponse_data["guid"]
    instance.data=json.dumps(movies_data)
    instance.save()  
    return True
@login_required(login_url="accounts:login")
@for_admin_only 
def add_movies(request):
    form =MoviesLibraryForm(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            images=request.FILES.getlist("image")
            instance.user=request.user
            summery=form.cleaned_data.get("summery")
            data={"summery":summery}
            instance.data=json.dumps(data)
            response=add_images_to_library(request,form,images,url_name="e-books",instance=instance)
            if response:
                add_movies_to_library(request,slug=instance.slug,instance=instance)
                return redirect(reverse("dashboard:uplaod_movie_video",kwargs={"slug":instance.slug})) 
    context={"form":form}
    return render(request,"dashboard_add_movies.html",context)

@login_required(login_url="accounts:login")
@check_user_validation  
def uplaod_movie_video(request,slug):
    movie=get_object_or_404(Movies,slug=slug,user=request.user,status="pending")
    form=MoviesVideoForm(request.POST or None,request.FILES or None)
    movie_data=json.loads(movie.data)
    if movie.check_movies():
        messages.error(request,"video is already uploaded")
        # return redirect(reverse("dashboard:movie",kwargs={"slug":video.my_course.slug}))
    else:
        if request.is_ajax():
            if form.is_valid():
                url = f"http://video.bunnycdn.com/library/{library_id}/videos/{movie.get_movies()['video_uid']}"
                print(url)
                file=form.cleaned_data.get("video")
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/*+json",
                    "AccessKey": AccessKey
                }
                response = requests.put( url, data=file, headers=headers)
                movie_url=f"https://iframe.mediadelivery.net/embed/{library_id}/{movie_data['video_uid']}?autoplay=false"
                movie_data["video"]=movie_url
                movie.data=json.dumps(movie_data)
                response = requests.get( url, headers=headers)
                data=response.json()
                movie.duration=int(data["length"])  
                movie.save()
                time=cache.get(f"dashoard_movie_email_{request.user}_{movie.id}")
                if time and time == True:
                    pass
                else:
                    body=f"movie edit for user {request.user.email}"
                    subject="edit movie"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    cache.set(f"dashoard_movie_email_{request.user}_{movie.id}",True,60*60*3)
                    messages.success(request,"Movie added successfully")
                return JsonResponse({"message":"1"})
            else:
                return FailedJsonResponse({"message":"1"})
    context={"form":form,"slug":movie.slug}
    return render(request,"dashboard_add_movie_video.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def movies(request):
    if request.user.is_superuser or request.user.is_director:
        movies=Movies.objects.all()
    else:
        movies=Movies.objects.filter(user=request.user)
    context={"movies":movies}
    return render(request,"dashboard_library_movies.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def check_movie(request,slug):
    movie=get_object_or_404(Movies,slug=slug,user=request.user)
    form=MoviesVideoForm(request.POST or None,request.FILES or None)
    movie_data=json.loads(movie.data)
    video_uid=movie_data["video_uid"]
    url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video_uid}"
    headers = {
                "Accept": "application/json",
                "Content-Type": "application/*+json",
                "AccessKey": AccessKey 
            }
    my_response = requests.get( url,headers=headers)
    try:
        data=my_response.json() 
        print(data)
        if data["length"] != 0 or data["encodeProgress"] == 100 or data["status"] != 0:
            print(data["status"])
            movie.duration=int(data["length"])
            movie_data["video"]=f"https://iframe.mediadelivery.net/embed/{library_id}/{data['guid']}?autoplay=false"
            movie.data=json.dumps(movie_data)
            movie.save()
            messages.success(request,"Movie Updated Successfully")
            return redirect(reverse("dashboard:movies"))
    except:
        pass
    if request.method == "POST":
        if form.is_valid():
            headers = {
            "Accept": "application/json",
                "AccessKey": AccessKey
                        }
            response = requests.delete( url,headers=headers)

            url = f"http://video.bunnycdn.com/library/{library_id}/videos"
            headers = {
            "Accept": "application/json",
            "Content-Type": "application/*+json",
            "AccessKey": AccessKey
        }
            json_url={"title":movie.slug,"collectionId":movie_data["collection_guid"]}
            response = requests.post( url,json=json_url,headers=headers)
            data=response.json()
            movie_data["video_uid"]=data["guid"]
            movie_data["video"]=f"https://iframe.mediadelivery.net/embed/{library_id}/{data['guid']}?autoplay=false"
            movie.data=json.dumps(movie_data)
            file=form.cleaned_data.get("video")
            url = f"http://video.bunnycdn.com/library/{library_id}/videos/{data['guid']}"
            headers = {
            "Accept": "application/json",
            "AccessKey": AccessKey}
            movie.save() 
            response = requests.put( url,data=file,headers=headers)
            data=my_response.json()
            print(data)
            movie.duration = int(data["length"])
            movie.save() 
            messages.success(request,"movie uploaded successfully")
            return JsonResponse({"message":"1"})
        else:
            return FailedJsonResponse({"message":"1"})
    context={"form":form,"slug":movie.slug}
    return render(request,"dashboard_library_check_movie.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def delete_movie(request,slug):
    movie=get_object_or_404(Movies,user=request.user,slug=slug)
    movie_data=json.loads(movie.data)
    url = f"http://video.bunnycdn.com/library/{library_id}/videos/{movie_data['video_uid']}"
    headers = {"Accept": "application/json",
               "AccessKey":AccessKey
               }
    response = requests.delete(url, headers=headers)
    movie.delete()
    messages.success(request,"movie deleted successfully")
    return redirect(reverse("dashboard:movies"))


@login_required(login_url="accounts:login")
@check_user_validation
def edit_movie(request,slug):
    movie=get_object_or_404(Movies,user=request.user,slug=slug)
    form =MoviesLibraryEditForm(request.POST or None,instance=movie)
    movie_data=json.loads(movie.data)
    form.initial["summery"]=movie_data["summery"]
    form.initial["price"]=movie.price
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            summery=form.cleaned_data.get("summery")
            if summery:
                movie_data["summery"]=summery
            image=form.cleaned_data.get("image")
            if image:
                headers = {
               "Accept": "*/*",
                   "AccessKey": Storage_Api
                        }
                file_url=f"https://storage.bunnycdn.com/{storage_name}/e-books/{movie.slug}/"
                response = requests.get(file_url, headers=headers) 

                data=response.json()
                for i in data:
                    print(i['ObjectName'])
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/e-books/{movie.slug}/{i['ObjectName']}"
                    response = requests.delete(image_url,headers=headers)
                    data=response.json()
                    print(data)
                images=request.FILES.getlist("image")
                for i in images:
                    headers = {  
                                "Accept": "*/*", 
                                "AccessKey":Storage_Api}
                    url=f"https://storage.bunnycdn.com/{storage_name}/e-books/{instance.slug}/{i}"
                    response = requests.put(url,data=i,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            image = f"https://{agartha_cdn}/e-books/{instance.slug}/{i}"
                            movie_data["images"]=[image]
                    except:
                        pass
            movie.data=json.dumps(movie_data)
            movie.status="pending"
            form.save()  
            messages.success(request,"movie edited successfully")
            return redirect(reverse("dashboard:uplaod_movie_video",kwargs={"slug":movie.slug}))
    context={"form":form,"movie":movie}
    return render(request,"dashboard_library_edit_movies.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def upload_demo_movie(request,slug):
    movie=get_object_or_404(Movies,slug=slug)
    form=MoviesVideoForm(request.POST or None,request.FILES or None)
    movie_data=json.loads(movie.data)
    if movie.check_demo_movies():
        return redirect(reverse("dashboard:movies"))
    if movie.check_movies() == False:
        messages.error(request,"upload movie first") 
        return redirect(reverse("dashboard:movies"))
    else:
        if request.is_ajax():
            if form.is_valid():
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/*+json",
                    "AccessKey": AccessKey
                }
                url = f"http://video.bunnycdn.com/library/{library_id}/videos"         
                data_2 = {"title":f"{slug}-demo","collectionId":movie.get_movies()["collection"]}
                response = requests.post( url, json=data_2, headers=headers)
                data_3=response.json()
                movie_data["demo_video_uid"]=data_3["guid"]
                
                url = f"http://video.bunnycdn.com/library/{library_id}/videos/{data_3['guid']}"
                file=form.cleaned_data.get("video")
                response = requests.put( url, data=file, headers=headers)
                movie_url=f"https://iframe.mediadelivery.net/embed/{library_id}/{data_3['guid']}?autoplay=false"
                movie_data["demo_video_url"]=movie_url
                movie.data=json.dumps(movie_data)
                response = requests.get( url, headers=headers)
                data=response.json()
                movie_data["demo_duration"]=int(data["length"])
                movie.data=json.dumps(movie_data)
                movie.save()
                messages.success(request,"Demo Movie added successfully")
                return JsonResponse({"message":"1"})
            else:
                return FailedJsonResponse({"message":"1"})
    context={"form":form,"slug":movie.slug}
    return render(request,"dashboard_add_demo_video.html",context) 


@login_required(login_url="accounts:login")
@check_user_validation
def check_demo_movie(request,slug):
    movie=get_object_or_404(Movies,slug=slug,user=request.user)
    form=MoviesVideoForm(request.POST or None,request.FILES or None)
    movie_data=json.loads(movie.data)
    video_uid=movie_data["demo_video_uid"]
    url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video_uid}"
    headers = {
                "Accept": "application/json",
                "Content-Type": "application/*+json",
                "AccessKey": AccessKey 
            }
    my_response = requests.get( url,headers=headers)
    try:
        data=my_response.json() 
        if data["length"] != 0 or data["encodeProgress"] == 100 or data["status"] != 0:
            print(data["encodeProgress"])
            movie_data["demo_duration"]=int(data["length"])
            movie_data["demo_video_url"]=f"https://iframe.mediadelivery.net/embed/{library_id}/{data['guid']}?autoplay=false"
            movie.data=json.dumps(movie_data)
            movie.save()
            messages.success(request,"Demo Movie Updated Successfully")
            return redirect(reverse("dashboard:movies"))
    except:
        pass
    if request.method == "POST":
        if form.is_valid():
            headers = {
            "Accept": "application/json",
                "AccessKey": AccessKey
                        }
            response = requests.delete( url,headers=headers)

            url = f"http://video.bunnycdn.com/library/{library_id}/videos"
            headers = {
            "Accept": "application/json",
            "Content-Type": "application/*+json",
            "AccessKey": AccessKey
        }
            json_url={"title":f"{movie.slug}-demo","collectionId":movie_data["collection_guid"]}
            response = requests.post( url,json=json_url,headers=headers)
            data=response.json()
            movie_data["demo_video_uid"]=data["guid"]
            movie_data["demo_video_url"]=f"https://iframe.mediadelivery.net/embed/{library_id}/{data['guid']}?autoplay=false"
            movie.data=json.dumps(movie_data)
            file=form.cleaned_data.get("video")
            url = f"http://video.bunnycdn.com/library/{library_id}/videos/{data['guid']}"
            headers = {
            "Accept": "application/json",
            "AccessKey": AccessKey}
            movie.save() 
            response = requests.put( url,data=file,headers=headers)
            data=my_response.json()
            movie_data["demo_duration"]= int(data["length"])
            movie.data=json.dumps(movie_data)
            movie.save() 
            messages.success(request,"Demo Movie uploaded successfully")
            return JsonResponse({"message":"1"})
        else:
            return FailedJsonResponse({"message":"1"})
    context={"form":form,"slug":movie.slug}
    return render(request,"dashboard_library_check_movie.html",context)



@login_required(login_url="accounts:login")
@check_user_validation
@check_movie_refund
def movie_refund(request,slug,id):   
    payment=get_object_or_404(Library_Payment,id=id)
    refund=Refunds.objects.create(type="movie_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","movie":payment.get_movies().name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    body=f"a new refund from user {request.user.email}"
    subject="new refund"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    messages.success(request,"Your Refund is Being Review By Admin")
    return redirect(reverse("dashboard:movies_payment"))




@login_required(login_url="accounts:login")
@check_if_there_payment_edited
def edit_movies_payment(request,slug,id):
    movie=get_object_or_404(Movies,slug=slug)
    payment=get_object_or_404(Library_Payment,id=id,status="declined")
    if payment.method != "Western Union":
        messages.error(request,"You Can't Edit This Payment Method")
        return redirect(reverse("accounts:movies_payment"))
    else:
        form=MoviesPaymentFom(request.POST or None ,request.FILES or None,instance=payment)
        form.initial["payment_image"]=None
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.status="pending"
                image=request.FILES.get("payment_image")
                if image:
                    url=f"https://storage.bunnycdn.com/{storage_name}/movies-payment/{movie.slug}/{payment.user.username}/{image}"
                    headers = {
                        "Content-Type": "application/octet-stream",
                        "AccessKey": Storage_Api
                    }
                    response = requests.put(url,data=image,headers=headers)
                    data=response.json()
                    try: 
                        if data["HttpCode"] == 201:
                            instance.payment_image = f"https://{agartha_cdn}/movies-payment/{movie.slug}/{payment.user.username}/{image}"
                            instance.save()
                    except:
                        pass                 
                instance.save()
                time=cache.get(f"dashoard_blog_email_{request.user}")
                if time and time == True:
                    pass
                else:
                    body=f"movie payment edit from user {request.user.email}"
                    subject="edit payment"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    cache.set(f"dashoard_movie_payment_email_{request.user}",True,60*60*3)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:movies_payment"))
    context={"form":form}
    return render(request,"dashboard_edit_movies_payment.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def movies_payment(request):
    if request.user.is_superuser:
        payments=Library_Payment.objects.filter(library_type=3).select_related("user").order_by("-id")
    else:
        payments=Library_Payment.objects.filter(user=request.user,library_type=3).select_related("user").order_by("-id")
    paginator = Paginator(payments, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dashboard_movies_payment.html",context)


@login_required(login_url="accounts:login")
@for_admin_only  
def paymob_movie_payment_refund(request,payment):
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
            refund=Refunds.objects.create(type="movie_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,status="approved")
            my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","movie":payment.get_movies().name}]}
            refund.data=json.dumps(my_data)
            refund.save()
            messages.success(request,"Payment Refunded")
        else:
            messages.error(request,"invalid payment refund")
    except:
        messages.error(request,"invalid payment refund")
