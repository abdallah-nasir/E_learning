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
from library.models import Library_Payment,Audio_Tracks,Audio_Book_Tracks,E_Book
from .models import *

from django.core.cache import cache 
from django.contrib.auth.decorators import user_passes_test
import json,requests
import datetime as today_datetime
from os.path import splitext
from datetime import datetime
from django.contrib.auth import get_user_model
User=get_user_model()
from E_learning.all_email import *
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
                cache_name.remove(data_check)
                if domain == None : 
                    cache.set("data",data,60*60*24*3)
                else:
                    cache.set("kemet_data",data,60*60*24*3)
        elif action == "add":
            cache_name=data[name]
            if number >= len(cache_name):
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
        while i['ObjectName'] == name: 
            response = requests.delete(image_url,headers=headers)
            data=response.json()
            break
    return data
class FailedJsonResponse(JsonResponse):
    def __init__(self, data):
        super().__init__(data)
        self.status_code = 400
@login_required(login_url="accounts:login") 
@check_user_validation   
def home(request):
    form=ChangeTeacherDataForm(request.POST or None,request.FILES or None,instance=request.user)
    form.initial["account_image"]=None
    form.initial["facebook"]=request.user.get_user_data()["facebook"]
    form.initial["linkedin"]=request.user.get_user_data()["linkedin"]
    form.initial["twitter"]=request.user.get_user_data()["twitter"]
    form.initial["title"]=request.user.get_user_data()["title"]
    form.initial["about_me"]=request.user.get_user_data()["about_me"]
    if request.method == 'POST':
        if form.is_valid():     
            instance=form.save(commit=False)
            try:
                if request.FILES["account_image"]:
                    file_name=request.FILES["account_image"]
                    url=f"https://storage.bunnycdn.com/{storage_name}/accounts/{instance.slug}/"
                    headers = {
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
                    response = requests.get(url, headers=headers) 
                    data=response.json()
                    for i in data:
                        url=f"https://storage.bunnycdn.com/{storage_name}/accounts/{instance.slug}/{i['ObjectName']}"
                        response = requests.delete(url,headers=headers)
                    url=f"https://storage.bunnycdn.com/{storage_name}/accounts/{instance.slug}/{file_name}"
                    file=form.cleaned_data.get("account_image")
                    response = requests.put(url,data=file,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            instance.account_image = f"https://{agartha_cdn}/accounts/{instance.slug}/{file_name}"
                            instance.save()
                    except:
                        pass
            except:
                pass
            facebook=form.cleaned_data.get('facebook')
            linkedin=form.cleaned_data.get('linkedin')
            twitter=form.cleaned_data.get('twitter')
            about_me=form.cleaned_data.get('about_me')
            title=form.cleaned_data.get('title')
            data={"social":[{"facebook":facebook,"linkedin":linkedin,"twitter":twitter}],
            "about_me":about_me,"title":title}
            instance.my_data=json.dumps(data)
            instance.save()
            # form=ChangeUserDataForm(instance=request.user)
            # form.initial["account_image"]=None
            messages.success(request,"Profile Updated Successfully")
    context={"form":form}
    return render(request,"dashboard_home.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def blog_payment(request):
    if request.user.is_superuser:
        payments=Blog_Payment.objects.all().order_by("-id")
    else:
        payments=Blog_Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(payments, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dashboard_blog_payment.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def course_payment(request):
    if request.user.is_superuser:
        courses=Payment.objects.all().order_by("-id")
    else:
        courses=Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dashboard_course_payment.html",context)



@login_required(login_url="accounts:login")
@check_user_validation
def consultant_payment(request):
    if request.user.is_superuser:
        consultant=Cosultant_Payment.objects.all().order_by("-id")
    else:
        consultant=Cosultant_Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(consultant, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dashboard_consultant_payment.html",context)

@login_required(login_url="accounts:login")  
@check_user_validation  
def blogs(request): 
    if request.user.account_type == 'teacher' and request.user.is_director == False and request.user.is_superuser == False:
        blogs=Blog.objects.filter(user=request.user).order_by("-id")
    else:
        blogs=Blog.objects.all().order_by("-id")
    paginator = Paginator(blogs, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj}
    return render(request,"dashboard_blogs.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def add_blog(request):
    blog_type_list=["standard","gallery","video","audio","quote","link"]
    try:
        type=request.GET["blog_type"]
        if type not in blog_type_list:
            return redirect(reverse("dashboard:blogs"))
        elif type == "link": 
            form=BlogLinkForm(request.POST or None,request.FILES or None)
        elif type == "quote":
            form=BlogQuoteForm(request.POST or None,request.FILES or None)
        elif type == "video" or type == "audio":
            form=AddBlog(request.POST or None,request.FILES or None)
        elif type == 'gallery':
            form=BlogGalleryForm(request.POST or None,request.FILES or None)
        else:
            form=AddBlog(request.POST or None,request.FILES or None)
        form_number=1
    except:
        form=BlogTypeForm(request.GET or None)
        form_number=2
    if request.method == "POST":
        if form_number == 1:
            if form.is_valid():
                instance=form.save(commit=False)
                instance.user=request.user
                instance.blog_type = type
                instance.save()
                if type == "link":
                    link=request.POST.get("link")
                    data={"link":link}
                    instance.data=json.dumps(data)
                elif type == "quote":
                    quote=request.POST.get("quote")
                    data={"quote":quote}
                    instance.data=json.dumps(data)
                elif type == "video":
                    blog_data={"collection":BLOGS_FOLDER_COLLECTIONID}
                    instance.data=json.dumps(blog_data)
                    url = f"http://video.bunnycdn.com/library/{library_id}/videos"    
                    data = {"title":instance.slug,"collectionId":BLOGS_FOLDER_COLLECTIONID}
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/*+json",
                        "AccessKey": AccessKey
                    }
                    response = requests.post( url, json=data, headers=headers)
                    data=response.json()
                    my_blog_data=json.loads(instance.data)
                    my_blog_data["video_guid"]=data["guid"]
                    instance.data=json.dumps(my_blog_data)
                tag=request.POST.get("tags")
                if tag: 
                    for i in tag.split(","):
                        tags,created=Tag.objects.get_or_create(name=i)
                        instance.tags.add(tags)
                        instance.save()
                image=request.FILES.getlist("image")
                count=0
                for i in image:
                    count +=1
                    image_extension=os.path.basename(i.name).split(".")[1]   
                    i.name=f"{instance.slug}-{count}.{image_extension}"
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/blogs/{instance.user}/{instance.slug}/{i}"
                    headers = {
                        "AccessKey": Storage_Api,
                    "Content-Type": "application/octet-stream",
                    }

                    response = requests.put(image_url,data=i,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            image_location = f"https://{agartha_cdn}/blogs/{instance.user}/{instance.slug}/{i}"
                            image=Blog_Images.objects.create(blog=instance,image=image_location)
                            instance.image.add(image)
                            instance.save()
                    except:
                        pass
                  
                if type =="video":
                    return redirect(reverse("dashboard:add_video_blog",kwargs={"slug":instance.slug}))
                elif type == "audio":
                    return redirect(reverse("dashboard:add_audio_blog",kwargs={"slug":instance.slug}))
                body=f"new blog from user {request.user.email}"
                subject="new blog"
                send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                messages.success(request,"Your Blog is Waiting for Admin Approve")
                return redirect(reverse("dashboard:blogs"))
        else:
            return redirect(reverse("dashboard:blogs"))
    context={"form":form,"form_number":form_number}
    return render(request,"dashboard_add_blog.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def edit_video_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    form=BlogVideoForm(request.POST or None,request.FILES or None)
    if request.is_ajax():
        if form.is_valid():
            my_blog_data=json.loads(blog.data)
            video_guid=my_blog_data["video_guid"]
            url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video_guid}"
            file=form.cleaned_data.get("video")
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/*+json",
                "AccessKey": AccessKey
            }
            response = requests.put(url,data=file, headers=headers)
            blog.video=f"https://iframe.mediadelivery.net/embed/{library_id}/{video_guid}?autoplay=false"
            response = requests.get( url, headers=headers)
            data=response.json()
            my_blog_data["video_length"]=0
            blog.data=json.dumps(my_blog_data)
            blog.save()
            body=f"edit blog from user {request.user.email}"
            subject="edit blog"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            messages.success(request,"Video added successfully")
            return JsonResponse({"message":"1"})
        else:
            return FailedJsonResponse({"message":"1"})
    context={"form":form,"blog":blog}
    return render(request,"dashboard_edit_video_blog.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
@check_blog_audio
def add_audio_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    form=BlogAudioForm(request.POST or None,request.FILES or None)
    if request.is_ajax():
        if form.is_valid():
            file=form.cleaned_data.get("video")
            url=f"https://storage.bunnycdn.com/{storage_name}/blogs-audio/{blog.slug}/{file}"
            headers = {
                    "Content-Type": "application/octet-stream",
                    "AccessKey": Storage_Api
                }
            response = requests.put(url,data=file,headers=headers)
            data=response.json()
            try: 
                if data["HttpCode"] == 201:
                    blog.video = f"https://{agartha_cdn}/blogs-audio/{blog.slug}/{file}"
                    blog.save()
            except:
                pass
            body=f"new blog from user {request.user.email}"
            subject="new blog"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            messages.success(request,"Audio added successfully")
            return JsonResponse({"message":"1","url":"/dashoard/blogs/"})
        else:
            messages.error(request,"invalid audio extensions")
            return FailedJsonResponse({"message":"1"})
    context={"form":form,"blog":blog}
    return render(request,"dashboard_add_audio_blog.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
@check_blog_video
def add_video_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    form=BlogVideoForm(request.POST or None,request.FILES or None)
    if request.is_ajax():
        if form.is_valid():
            # instance=form.save(commit=False)
            my_blog_data=json.loads(blog.data)
            video_guid=my_blog_data["video_guid"]
            url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video_guid}"
            file=form.cleaned_data.get("video")
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/*+json",
                "AccessKey": AccessKey
            }
            response = requests.put( url, data=file, headers=headers)
            blog.video=f"https://iframe.mediadelivery.net/embed/{library_id}/{video_guid}?autoplay=false"
            response = requests.get( url, headers=headers)
            data=response.json()
            my_blog_data["video_length"]=0
            blog.data=json.dumps(my_blog_data)
            blog.save()
            body=f"new blog from user {request.user.email}"
            subject="new blog"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            messages.success(request,"Video added successfully")
            return JsonResponse({"message":"1"})
        else:
            return FailedJsonResponse({"message":"1"})
    context={"form":form,"blog":blog}
    return render(request,"dashboard_add_video_blog.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
@check_blog_audio
def check_audio_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    url=f"https://storage.bunnycdn.com/{storage_name}/blogs-audio/{blog.slug}/"
    headers = {
        "Accept": "*/*", 
        "AccessKey":Storage_Api}
    response = requests.get(url, headers=headers) 
    try:
        data=response.json()
        audio_guid=data[-1]["Guid"]
        name=data[-1]["ObjectName"]
        blog.data=json.dumps({"audio_guid":audio_guid})
        blog.video = f"https://{agartha_cdn}/blogs-audio/{blog.slug}/{name}"
        blog.save()
        messages.success(request,"audio uploaded successfully")
        return redirect(reverse("dashboard:blogs"))
    except:
        return redirect(reverse("dashboard:add_audio_blog",kwargs={"slug":slug}))


@login_required(login_url="accounts:login")
@check_blog_video 
@check_blog_video_progress
def check_blog_video(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    form=BlogVideoForm(request.POST or None,request.FILES or None)
    blog_data=json.loads(blog.data)
    video_uid=blog_data["video_guid"] 
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
            blog_data["video_length"] =data["length"]
            blog.data=json.dumps(blog_data)
            blog.save()
            messages.success(request,"Video Updated Successfully")
            return redirect(reverse("dashboard:blogs"))
    except:
        pass
    if request.method == "POST":
        if form.is_valid():
            if data["encodeProgress"] !=100:
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
                json_url={"title":blog.slug,"collectionId":BLOGS_FOLDER_COLLECTIONID}
                response = requests.post( url,json=json_url,headers=headers)
                data=response.json()
                blog_data["video_guid"]=data["guid"]
                blog.video=f"https://iframe.mediadelivery.net/embed/{library_id}/{data['guid']}?autoplay=false"
                file=form.cleaned_data.get("video")
                url = f"http://video.bunnycdn.com/library/{library_id}/videos/{data['guid']}"
                headers = {
                "Accept": "application/json",
                "AccessKey": AccessKey}
                response = requests.put( url,data=file,headers=headers)
                data=my_response.json()
                blog_data["video_length"] = data["length"]
                blog.save()
                messages.success(request,"video uploaded successfully")
                return JsonResponse({"message":"1"})
               
            else:
                return FailedJsonResponse({"message":"1"})
        else:
            return FailedJsonResponse({"message":"1"})

    return render(request,"dashboard_check_blog_video.html",{"blog":blog})
@login_required(login_url="accounts:login")
@check_user_validation
def edit_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug,user=request.user)
    type=blog.blog_type
    if type == "link":
        form=BlogLinkForm(request.POST or None,request.FILES or None,instance=blog)
        form.initial["link"] = blog.get_link()
    elif type == "quote":
        form=BlogQuoteForm(request.POST or None,request.FILES or None,instance=blog)
        form.initial["quote"]=blog.get_quote()
    elif type == "video" or type == "audio":
        form=AddBlog(request.POST or None,request.FILES or None,instance=blog)
    elif type == 'gallery':
        form=BlogGalleryForm(request.POST or None,request.FILES or None,instance=blog)
    else:
        form=AddBlog(request.POST or None,request.FILES or None,instance=blog)

    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.approved=False
            tag=form.cleaned_data.get("tags")
            tag_list=[]
            if tag:
                for i in tag:
                    tag_list.append(i)
                    if i in blog.tags.all():
                        pass
                    else:
                        new_tags,created=Tag.objects.get_or_create(name=i)
                        instance.tags.add(new_tags)
                        instance.save()
                for i in instance.tags.all():
                    if i.name in tag_list:
                        pass
                    else:
                        instance.tags.remove(i)
            image=form.cleaned_data.get("image")
            if image:
                if  blog.blog_type != "gallery":
                    if len(blog.image.all()) > 0:
                        messages.error(request,"delete current image first")
                        return redirect(reverse("dashboard:edit_blog",kwargs={"slug":blog.slug}))
                    else:
                        image_extension=os.path.basename(image.name).split(".")[1]   
                        image.name=f'{instance.slug}.{image_extension}'
                        image_url=f"https://storage.bunnycdn.com/{storage_name}/blogs/{instance.user.username}/{instance.slug}/{image}"
                        headers = {
                            "AccessKey": Storage_Api,
                        "Content-Type": "application/octet-stream",
                        }

                        response = requests.put(image_url,data=image,headers=headers)
                        data=response.json()
                        try:
                            if data["HttpCode"] == 201:
                                image_location = f"https://{agartha_cdn}/blogs/{instance.user}/{instance.slug}/{image}"
                                image=Blog_Images.objects.create(blog=instance,image=image_location)
                                instance.image.add(image)
                                instance.save()
                        except:
                            pass
                elif blog.blog_type =="gallery":
                    count=0
                    for i in image:
                        count +=1
                        image_extension=os.path.basename(i.name).split(".")[1]   
                        i.name=f'{instance.slug}-{count}.{image_extension}'
                        image_url=f"https://storage.bunnycdn.com/{storage_name}/blogs/{instance.user.username}/{instance.slug}/{i}"
                        headers = {
                            "AccessKey": Storage_Api,
                        "Content-Type": "application/octet-stream",
                        }

                        response = requests.put(image_url,data=i,headers=headers)
                        data=response.json()
                        try:
                            if data["HttpCode"] == 201:
                                image_location = f"https://{agartha_cdn}/blogs/{instance.user}/{instance.slug}/{i}"
                                image=Blog_Images.objects.create(blog=instance,image=image_location)
                                instance.image.add(image)
                                instance.save()
                        except:
                            pass
            instance.status="pending"
            instance.save()
            if instance.blog_type == "audio":
                return redirect(reverse("dashboard:edit_audio_blog",kwargs={"slug":slug}))
            elif instance.blog_type == "video":
                return redirect(reverse("dashboard:edit_video_blog",kwargs={"slug":slug}))
            time=cache.get(f"dashoard_blog_email_{request.user}")
            if time and time == True:
                pass
            else:
                body=f"blog edit from user {request.user.email}"
                subject="edit blog"
                send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                cache.set(f"dashoard_blog_email_{request.user}",True,60*60*3)
            if instance.domain_type == 2:
                change_cache_value(request,name="blogs",data_check=instance,action="remove",domain="kemet")
                change_blog_cache(request,data_check=instance,action="remove",domain="kemet")
            else:
                change_cache_value(request,name="blogs",data_check=instance,action="remove")
                change_blog_cache(request,data_check=instance,action="remove")
            messages.success(request,"Your Blog is Waiting for Admin Approve")
            return redirect(reverse("dashboard:blogs"))
    context={"blog":blog,"form":form}
    return render(request,"dashboard_edit_blog.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def edit_audio_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug,user=request.user,status="pending")
    form=BlogAudioForm(request.POST or None,request.FILES or None)
    if request.is_ajax():
        if form.is_valid():
            file=form.cleaned_data.get("video")
            url=f"https://storage.bunnycdn.com/{storage_name}/blogs-audio/{blog.slug}/{file}"
            headers = {
                    "Content-Type": "application/octet-stream",
                    "AccessKey": Storage_Api
                }
            response = requests.put(url,data=file,headers=headers)
            data=response.json()
            blog.status="pending"
            blog.save()
            try: 
                if data["HttpCode"] == 201:
                    blog.video = f"https://{agartha_cdn}/blogs-audio/{blog.slug}/{file}"
                    blog.save()
            except:
                pass
            
            body=f"edit blog from user {request.user.email}"
            subject="edit blog"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            messages.success(request,"Audio added successfully")
            return JsonResponse({"message":"1","url":"/dashoard/blogs/"})
        else:
            messages.error(request,"invalid audio extensions")
            return FailedJsonResponse({"message":"1"})
    context={"form":form,"blog":blog}
    return render(request,"dashboard_edit_audio_blog.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def delete_blog_image(request,id):
    image=get_object_or_404(Blog_Images,id=id)
    if image.blog.user == request.user:
        headers = {
            "AccessKey": Storage_Api,
            "Content-Type": "application/octet-stream",
        }   
        name=os.path.basename(image.image.name)  
        file_url=f"https://storage.bunnycdn.com/{storage_name}/blogs/{request.user.username}/{image.blog.slug}/"
        image_url=f"https://storage.bunnycdn.com/{storage_name}/blogs/{request.user.username}/{image.blog.slug}/{name}"
        response=delete_image(request,image_url=image_url,name=name,file_url=file_url,headers=headers)
        try:
            if response["HttpCode"] == 200:
                image.delete()
        except:
            pass
    return redirect(reverse("dashboard:edit_blog",kwargs={"slug":image.blog.slug}))

@login_required(login_url="accounts:login")
@check_user_validation
def delete_blog_video(request,id):
    blog=get_object_or_404(Blog,id=id)
    if blog.user == request.user:
        blog.video.delete()
    return redirect(reverse("dashboard:edit_blog",kwargs={"slug":blog.slug}))

@login_required(login_url="accounts:login")
@check_user_validation
def delete_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    if request.user == blog.user:
        try:
            blog_data=json.loads(blog.data)
            video_uid=blog_data["video_guid"]
            url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video_uid}"
            headers = {
            "Accept": "application/json",
            "AccessKey": AccessKey
                        }
            response = requests.delete( url,headers=headers)
            blog.delete()
            messages.success(request,"blog deleted successfully")
        except:
            blog.delete()
            messages.success(request,"blog deleted successfully")
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:blogs"))
    return redirect(reverse("dashboard:blogs"))

@login_required(login_url="accounts:login")
@check_user_validation
def courses(request):
    if request.user.account_type == 'teacher' and request.user.is_director == False and request.user.is_superuser == False:
        courses=Course.objects.filter(Instructor=request.user).order_by("-id")
    else:
        courses=Course.objects.all().order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"courses":page_obj}
    return render(request,"dashboard_course.html",context)
   
@login_required(login_url="accounts:login")
@check_user_validation
def edit_course(request,slug):
    course=get_object_or_404(Course,slug=slug)
    form=EditCourse(request.POST or None , request.FILES or None,instance=course)
    form.initial["image"]=None
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.status = "pending"
                if form.cleaned_data.get("image"):
                    current_image=course.image.name
                    current_image_name=os.path.basename(current_image)  
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/courses/{instance.slug}/{current_image_name}"
                    file_url=f"https://storage.bunnycdn.com/{storage_name}/courses/{instance.slug}/"
                    headers = {
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
                    delete_image(request,file_url=file_url,image_url=image_url,headers=headers,name=current_image_name)
                    image=form.cleaned_data.get("image")
                    image_path=os.path.basename(image.name).split(".")[1]
                    image.name=f"{instance.slug}.{image_path}"
                    url=f"https://storage.bunnycdn.com/{storage_name}/courses/{instance.slug}/{image}"
                    headers = {
                        "AccessKey": Storage_Api,
                        "Content-Type": "application/octet-stream",
                        }    
                    response = requests.put(url,data=image,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            instance.image = f"https://{agartha_cdn}/courses/{instance.slug}/{image}"
                            instance.save()
                    except:
                        pass
                instance.save()
                time=cache.get(f"dashoard_course_email_{request.user}")
                if time and time == True:
                    pass
                else:
                    body=f"course edit from user {request.user.email}"
                    subject="edit course"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    cache.set(f"dashoard_course_email_{request.user}",True,60*60*3)
                    if instance.domain_type == 2:
                        change_cache_value(request,name="courses",data_check=instance,action="remove",domain="kemet")
                    else:
                        change_cache_value(request,name="courses",data_check=instance,action="remove")

                messages.success(request,"Course Edited Successfully")
                return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:courses"))
    context={"course":course,"form":form}
    return render(request,"dashboard_course_edit.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def edit_course_image(request,id):
    course=get_object_or_404(Course,id=id)
    if request.user == course.Instructor:
        course.image=""
        course.save()
        url = f"https://storage.bunnycdn.com/{storage_name}/{course.slug}/{course.slug}"
        headers = {"AccessKey":Storage_Api}
        response = requests.delete( url, headers=headers)
    return redirect(reverse("dashboard:edit_course",kwargs={"slug":course.slug}))
 
@login_required(login_url="accounts:login")
@check_user_validation
def add_course(request):
    form=AddCourse(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.Instructor=request.user
            instance.image=None
            instance.save()
            file_name=request.FILES["image"]
            image_url=f"https://storage.bunnycdn.com/{storage_name}/courses/{instance.slug}/{file_name}"
            headers = {
                "AccessKey": Storage_Api,
                "Content-Type": "application/octet-stream",
                }

            file=form.cleaned_data.get("image")
            response = requests.put(image_url,data=file,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    instance.image = f"https://{agartha_cdn}/courses/{instance.slug}/{file_name}"
                    
                    instance.save()
            except:
                pass
            url = f"http://video.bunnycdn.com/library/{library_id}/collections"
            json = {"name":instance.slug}
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/*+json",
                "AccessKey": AccessKey
            }
            response = requests.post( url, json=json, headers=headers)
            data=response.json()
            instance.collection=data["guid"]
            instance.save()
            body=f"new course from user {request.user.email}"
            subject="new course"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            messages.success(request,"course added successfully")
            return redirect(reverse("dashboard:add_video",kwargs={"slug":instance.slug}))
    context={"form":form}
    return render(request,"dashboard_add_course.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def videos(request,slug):
    videos=Videos.objects.filter(my_course__slug=slug,user=request.user).order_by("-id")
    context={"videos":videos,"slug":slug}
    return render(request,"dashboard_videos.html",context)

@login_required(login_url="accounts:login")
@admin_director_check
def course_videos(request,id):
    videos=Videos.objects.filter(my_course=id).order_by("-id")
    context={"videos":videos,"library_id":library_id}
    return render(request,"dashboard_course_videos.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def delete_videos(request,slug):
    video=get_object_or_404(Videos,slug=slug)
    if request.user == video.user:
        url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video.video_uid}"
        headers = {
        "Accept": "application/json",
        "AccessKey": AccessKey
                }
        response = requests.delete( url, headers=headers)
        video.my_course.duration -=video.duration
        video.my_course.save()
        video.delete()
        messages.success(request,"Video deleted successfully")
        return redirect(reverse("dashboard:videos",kwargs={"slug":video.my_course.slug}))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:home"))

@login_required(login_url="accounts:login")
@check_user_validation
def edit_videos(request,slug):
    video=get_object_or_404(Videos,slug=slug)
    if request.user == video.user and video.my_course.status !="pending":
        form=EditVideo(request.POST or None,instance=video)
        if request.method == "POST":
            instance=form.save(commit=False)    
            instance.my_course.status = "pending"  
            instance.my_course.save()
        
            instance.save()
            if video.my_course.domain_type == 2:
                change_cache_value(request,name="courses",data_check=video.my_course,action="remove",domain="kemet")
            else:
                change_cache_value(request,name="courses",data_check=video.my_course,action="remove")
            messages.success(request,"video edited successfully")
            return redirect(reverse("dashboard:videos",kwargs={"slug":video.my_course.slug}))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:home"))
    context={"form":form}
    return render(request,"dashboard_edit_video.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
@check_if_teacher_have_pending_video_upload
def add_video(request,slug):
    form=AddVideo(request.POST or None)
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.user=request.user
                instance.my_course=course
                instance.save()
                instance.my_course.videos.add(instance)
                instance.my_course.status ="pending"
                instance.my_course.save()
                url = f"http://video.bunnycdn.com/library/{library_id}/videos"         
                json = {"title":instance.slug,"collectionId":instance.my_course.collection}
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/*+json",
                    "AccessKey": AccessKey
                }
                response = requests.post( url, json=json, headers=headers)
                data=response.json()
                instance.video_uid=data["guid"]
                instance.save()
                return redirect(reverse("dashboard:complete_add_video",kwargs={"slug":instance.slug}))
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:blogs"))
    context={"form":form,"course":course.slug}
    return render(request,"dashboard_add_video.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def complete_add_video(request,slug):
    video=get_object_or_404(Videos,slug=slug,user=request.user)
    form=UploadVideoForm(request.POST or None,request.FILES or None)
    if video.video or video.duration > 0:
        messages.error(request,"video is already uploaded")
        return redirect(reverse("dashboard:videos",kwargs={"slug":video.my_course.slug}))
    else:
        if request.is_ajax():
            if form.is_valid():
                url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video.video_uid}"
                file=form.cleaned_data.get("video")
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/*+json",
                    "AccessKey": AccessKey
                }
                response = requests.put( url, data=file, headers=headers)
                video.video=f"https://iframe.mediadelivery.net/embed/{library_id}/{video.video_uid}?autoplay=false"
                response = requests.get( url, headers=headers)
                data=response.json()
                video.duration=data["length"]  
                video.save()
                video.total_duration()
                messages.success(request,"Video added successfully")
                return JsonResponse({"message":"1"})
            else:
                return FailedJsonResponse({"message":"1"})
    context={"form":form,"video":video.slug,"slug":video.my_course.slug}
    return render(request,"dashboard_complete_video_upload.html",context)
@login_required(login_url="accounts:login")
@check_user_validation
def check_video(request,slug):
    video=get_object_or_404(Videos,slug=slug)
    if request.user == video.user and video.duration == 0:
        form=UploadVideoForm(request.POST or None,request.FILES or None)
        url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video.video_uid}"
        headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/*+json",
                    "AccessKey": AccessKey
                }
        my_response = requests.get( url,headers=headers)
        data=my_response.json() 
        if data["length"] != 0 or data["encodeProgress"] == 100 or data["status"] != 0:
            video.duration=data["length"]
            video.video=f"https://iframe.mediadelivery.net/embed/{library_id}/{video.video_uid}?autoplay=false"
            video.save()       
            video.total_duration()
            messages.success(request,"Video Updated Successfully")
            return redirect(reverse("dashboard:videos",kwargs={"slug":video.my_course.slug}))
        if request.method == "POST":
            if form.is_valid():
                if video.duration != 0:
                    messages.error(request,"video is already uploaded")
                    return redirect(reverse("dashboard:videos",kwargs={"slug":video.my_course.slug}))
                if data["encodeProgress"] !=100:
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
                    json={"title":video.slug,"collectionId":video.my_course.collection}
                    response = requests.post( url,json=json,headers=headers)
                    data=response.json()
                    video.video_uid=data["guid"]
                    video.video="https://iframe.mediadelivery.net/embed/{library_id}/{instance.video_uid}?autoplay=false"
                    video.save()
                    file=form.cleaned_data.get("video")
                    url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video.video_uid}"
                    headers = {
                    "Accept": "application/json",
                    "AccessKey": AccessKey}
                    response = requests.put( url,data=file,headers=headers)
                    data=my_response.json()
                    video.duration = data["length"]
                    video.save()
                    video.total_duration()
                    messages.success(request,"Video Uploaded Successfully")
                    return JsonResponse({"message":"1"})
            else:
                return FailedJsonResponse({"message":"1"})

    else:
        messages.error(request,"video is already uploaded")
        return redirect(reverse("dashboard:videos",kwargs={"slug":video.my_course.slug}))
    context={"form":form,"video":video}
    return render(request,"dashboard_check_video.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def get_video_length(request,id):
    video=get_object_or_404(Videos,id=id)
    if request.user == video.user:
        if video.video:
            if video.duration <=0:
                url = f"http://video.bunnycdn.com/library/{library_id}/videos/{video.video_uid}"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/*+json",
                    "AccessKey": AccessKey
                }
                response = requests.get( url,headers=headers)
                data=response.json()
                video.duration=data["length"]
                video.save()
                video.my_course.duration +=video.duration
                video.my_course.save()
                messages.success(request,"Video updated successfully")
    return redirect(reverse("dashboard:videos",kwargs={"slug":video.my_course.slug}))
@login_required(login_url="accounts:login")
@check_user_validation
def events(request):
    if request.user.account_type == "teacher" and request.user.is_director == False and request.user.is_superuser == False:
        events=Events.objects.filter(user=request.user).order_by("-id")
    else:
        events=Events.objects.all().order_by("-id")
    context={"events":events}
    return render(request,"dashboard_events.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
@check_if_teacher_has_event
def add_event(request):
    translation.deactivate()
    form=AddEvent(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)  
            start=request.POST.get("start_time")
            end=request.POST.get("end_time")
            instance.start_time=datetime.strptime(f"{start}","%I:%M:%S %p").time()
            instance.end_time=datetime.strptime(f"{end}","%I:%M:%S %p").time()
            instance.user=request.user
            instance.image=None
            image=form.cleaned_data.get("image")
            instance.save() 
            image_extension=os.path.basename(image.name).split(".")[1]   
            image.name=f"{instance.slug}.{image_extension}"
            image_url=f"https://storage.bunnycdn.com/{storage_name}/events/{instance.user.username}/{image}"
            headers = {
                    "AccessKey": Storage_Api,
                    "Content-Type": "application/octet-stream",
                    }

            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    instance.image = f"https://{agartha_cdn}/events/{instance.user.username}/{image.name}"
            except:
                pass
            zoom=form.cleaned_data.get("zoom_link")
            details=form.cleaned_data.get("details")
            data={'zoom':zoom,"details":details}
            instance.details=json.dumps(data)  
            instance.save() 
            body=f"new event from user {request.user.email}"
            subject="new event"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            messages.success(request,"Event added successfully")
            return redirect("dashboard:events")
    context={"form":form}
    return render(request,"dashboard_add_events.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def edit_event(request,id):
    event=get_object_or_404(Events,id=id)
    if event.status == "start" or event.status =="completed":
        return redirect(reverse("dashboard:events"))
    form=Edit_event(request.POST or None,request.FILES or None,instance=event)
    form.initial["image"]=None
    form.initial["details"]=event.get_details()["details"]
    form.initial["zoom_link"]=event.get_details()["zoom"]
    if request.user == event.user:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                start=request.POST.get("start_time")
                end=request.POST.get("end_time")
                instance.start_time=datetime.strptime(f"{start}","%I:%M:%S %p").time()
                instance.end_time=datetime.strptime(f"{end}","%I:%M:%S %p").time()
                zoom=form.cleaned_data.get("zoom_link")
                details=form.cleaned_data.get("details")
                data={'zoom':zoom,"details":details}
                instance.details=json.dumps(data)  
                instance.status="pending"
                if form.cleaned_data.get("image"):
                    current_image=event.image.name
                    current_image_name=os.path.basename(current_image)  
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/events/{instance.user.username}/{current_image_name}"

                    headers = {
                            "AccessKey": Storage_Api,
                            "Content-Type": "application/octet-stream",
                            }
                    file_url=f"https://storage.bunnycdn.com/{storage_name}/events/{instance.user.username}/"
                    delete_image(request,file_url=file_url,image_url=image_url,headers=headers,name=current_image_name)
                    image=form.cleaned_data.get("image")
                    image_extension=os.path.basename(image.name).split(".")[1]   
                    image.name=f"{instance.slug}.{image_extension}"
                    new_image_url=f"https://storage.bunnycdn.com/{storage_name}/events/{instance.user.username}/{image}"
                    response = requests.put(url=new_image_url,data=image,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            instance.image = f"https://{agartha_cdn}/events/{instance.user.username}/{image}"
                    except:
                        pass
                instance.get_similar_event()
                instance.save() 
                time=cache.get(f"dashoard_event_email_{request.user}")
                if time and time == True:
                    pass
                else:
                    body=f"event edit from user {request.user.email}"
                    subject="event edit"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    cache.set(f"dashoard_event_email_{request.user}",True,60*60*3)
                change_cache_value(request,name="events",data_check=instance,action="remove")
                messages.success(request,"Event updated successfully")
                return redirect("dashboard:events")
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:events")
    context={"form":form,"event":event}
    return render(request,"dashboard_edit_event.html",context)




    return redirect(reverse("dashboard:edit_event",kwargs={"id":event.id}))
@login_required(login_url="accounts:login")
@check_user_validation
def delete_event(request,id):
    event=get_object_or_404(Events,id=id)
    if request.user == event.user:
        event.delete()
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:events")
    return redirect(reverse("dashboard:events"))

@login_required(login_url="accounts:login")
@check_user_validation
def demo_event(request,id):
    event=get_object_or_404(Events,id=id,status="pending")
    context={"event":event}
    return render(request,"dashboard_demo_event.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def finish_event(request,id):
    event=get_object_or_404(Events,id=id)
    if request.user == event.user:
        event.status = "completed"
        event.save()
        messages.success(request,"Event End Successfully")
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:events")
    return redirect(reverse("dashboard:events"))
@login_required(login_url="accounts:login")
@check_user_validation
def start_event(request,slug):
    event=get_object_or_404(Events,slug=slug,status="approved")
    if request.user == event.user:
        emails=event.get_students_events()
        # html="dashboard_events.html"

        event.status="start"
        event.save()
        change_cache_value(request,name="blogs",data_check=event,action="remove")
        messages.success(request,"Event Has Been Started")
    else:
        messages.error(request,"invalid event status")
        return redirect(reverse("dashboard:events"))
    return redirect(reverse("dashboard:events"))

@login_required(login_url="accounts:login")
@check_user_validation
def quiz(request,slug):
    course=get_object_or_404(Course,slug=slug)
    if request.user.is_director or request.user.is_superuser or request.user == course.Instructor:
        pass
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"quiz":course.quiz,"course":course}
    return render(request,"dashboard_quiz.html",context)


@login_required(login_url="accounts:login")
@check_user_validation
def add_quiestions(request,slug):
    form=AddQuestion(request.POST or None)
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid(): 
                instance=form.save(commit=False)
                instance.save() 
                if course.quiz == None:
                   quiz=Quiz.objects.create(course_id=course.id)
                   quiz.questions.add(instance)
                   quiz.save()
                   course.quiz=quiz
                   course.course_status = "on process"
                   course.save()
                else:
                    course.quiz.questions.add(instance)
                    course.quiz.save()
                messages.success(request,"Question added successfully")
                return redirect(reverse("dashboard:add_answer",kwargs={"course":course.slug,"slug":instance.slug}))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_add_question.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def edit_quiestions(request,course,slug):
    course=get_object_or_404(Course,slug=course)
    if course.quiz:
        try:
            question=course.quiz.questions.get(slug=slug)
        except:
            messages.error(request,"invalid question")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"invalid question")
        return redirect(reverse("dashboard:courses"))
    form=AddQuestion(request.POST or None,instance=question)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                course.course_status = "on process"
                course.save()
                instance.save() 
                messages.success(request,"Question Edited successfully")
                return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_edit_question.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def delete_question(request,slug,id):
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        try:
            course.quiz.questions.get(id=id).delete()
            # if  course.quiz.questions.count() == 0:
                # course.quiz.delete()
                # return redirect(reverse("dashboard:courses"))
        except:
            messages.error(request,"invalid question")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:courses")
    return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))


@login_required(login_url="accounts:login")
@check_user_validation
def add_answer(request,course,slug):
    form=AddAnswer(request.POST or None)
    course=get_object_or_404(Course,slug=course)
    if course.quiz:
        try:
            question=course.quiz.questions.get(slug=slug)
        except:
            messages.error(request,"invalid question")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"invalid question")
        return redirect(reverse("dashboard:courses"))
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.question=question
                course.course_status = "on process"
                course.save()
                instance.save() 
                question.answer.add(instance)
                course.quiz.answers.add(instance)
                course.quiz.save()
                question.save()
                messages.success(request,"Answer added successfully")
                return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug})) 
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_add_answer.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def edit_answer(request,course,id):
    course=get_object_or_404(Course,slug=course,Instructor=request.user)
    if course.quiz:
        try:
            answer=course.quiz.answers.get(id=id)
        except:
            messages.error(request,"invalid answer")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"invalid question")
        return redirect(reverse("dashboard:courses"))
    form=AddAnswer(request.POST or None,instance=answer)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                course.course_status = "on process"
                course.save()
                instance.save() 
                messages.success(request,"Answer Edited successfully")
                return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_edit_answer.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def delete_answer(request,slug,id):
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        try:
            course.quiz.answers.get(id=id).delete()
            # if  course.quiz.questions.count() == 0:
            #     course.quiz.delete()
        except:
            messages.error(request,"invalid answer")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:courses")
    return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))

@login_required(login_url="accounts:login")
@admin_director_check
def teachers(request):
    teacher=User.objects.filter(account_type="teacher").order_by("-id")
    paginator = Paginator(teacher, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"teachers":page_obj}
    return render(request,"dashboard_teachers.html",context)


@login_required(login_url="accounts:login")
@for_admin_only
def approve(request):
    if request.user.is_superuser :
        try:
            qs=request.GET["approve"]
            choices={"Teachers":"teacher","Blogs":"blogs","Blog Payments":"blog_payment","Consultant Payment":"consultant_payment",
                "Course":"course","Course Payments":"payment","Events":"events","movies":"movies"}
            if qs == "blogs":
                query=Blog.objects.filter(status="pending").order_by("-id")
            elif qs == "blog_payment":  
                query=Blog_Payment.objects.filter(status="pending",expired=False).order_by("-id")
            elif qs == "consultant_payment": 
                query=Cosultant_Payment.objects.filter(status="pending",expired=False).order_by("-id")
            elif qs == "course":
                query=Course.objects.filter(status="pending").order_by("-id")
            elif qs == "events":
                query=Events.objects.filter(status="pending").order_by("-id")
            elif qs == "payment":
                query=Payment.objects.filter(status="pending",expired=False).order_by("-id")
            elif qs == "teacher":
                query=TeacherForms.objects.filter(status="pending").order_by("-id")
            elif qs == "add_user":
               query= AddStudentCourse.objects.filter(status="pending").order_by("-id")
            elif qs == "movies":
                query= Movies.objects.filter(status="pending").order_by("-id")
            elif qs == "audios":
                query= Audio_Tracks.objects.filter(status="pending").order_by("-id")
            elif qs == "movie_payment":
                query= Library_Payment.objects.filter(status="pending",library_type=3,expired=False).order_by("-id")
            elif qs == "audio_book":
                query= Audio_Book_Tracks.objects.filter(status="pending").order_by("-id")
            elif qs == "audio_payment":
                query= Library_Payment.objects.filter(status="pending",library_type=2,expired=False).order_by("-id")
            elif qs == "e_book":
                    query= E_Book.objects.filter(status="pending").order_by("-id")
            elif qs == "audio_book_payment":
                query= Library_Payment.objects.filter(status="pending",library_type=1,expired=False).order_by("-id")
            elif qs == "e_book_payment":
                query= Library_Payment.objects.filter(status="pending",library_type=4,expired=False).order_by("-id")
            else:
                query=False
        except:
            return redirect(reverse("dashboard:home"))

    else:
        messages.error(request,"You Don't have Permission")
        return redirect(reverse("dashboard:home"))
    context={"query":query,"qs":qs,"choices":choices}
    return render(request,"dashboard_approve.html",context)

@login_required(login_url="accounts:login")
def show_demo_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    if blog.status == "approved":
        return redirect(reverse("dashboard:blogs"))
    if request.user.is_director or request.user.is_superuser or request.user == blog.user:  
        pass
    else:
        messages.error(request,"you dont have permission")
        return redirect(reverse("dashboard:home"))
    context={"blog":blog}
    return render(request,"dashboard_show_demo_blog.html",context)

@login_required(login_url="accounts:login")
@for_admin_only
def approve_content(request,id):
    if request.user.is_superuser:
        try:
            qs=request.GET["approve"]
            if qs == "blogs":
                query=get_object_or_404(Blog,id=id,status="pending")
                query.status="approved"
                query.save()
                if query.domain_type == 2:
                    change_cache_value(request,name="blogs",data_check=query,action="add",number=4,domain="kemet")
                    change_blog_cache(request,data_check=query,action="add",domain="kemet")
                else:
                    change_cache_value(request,name="blogs",data_check=query,action="add",number=4)
                    change_blog_cache(request,data_check=query,action="add")   
                messages.success(request,"Blog Approved Successfully")
            if qs == "blog_payment":
                query=get_object_or_404(Blog_Payment,id=id,status="pending")
                query.created_at= today_datetime.date.today()
                data=json.loads(query.data)
                if data["type"] == "agartha":
                    query.add_time_expired_to_related_course()
                    query.user.vip = True
                elif data["type"] == "kemet":
                    query.add_time_expired_to_related_course_kemet()
                    query.user.is_kemet_vip=True
                query.status="approved"
                if data["type"] == "agartha":
                    for i in Blog_Payment.objects.filter(user=request.user,type=1,expired=False).exclude(id=query.id).select_related("user"):
                        i.expired=True
                        i.save()
                else:
                    for i in Blog_Payment.objects.filter(user=request.user,type=2,expired=False).exclude(id=query.id).select_related("user"):
                        i.expired=True
                        i.save()
                query.user.save()
                query.save()                    
                
                send_mail(
                'Payment Completed',
                "Successfull Payment",
                PAYMENT_EMAIL_USERNAME,
                [query.user.email,FINANCE_EMAIL_USERNAME],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
                messages.success(request,"Payment Approved Successfully")
            if qs == "consultant_payment":
                query=get_object_or_404(Cosultant_Payment,id=id,status="pending")
                query.status="approved"
                consult=Consultant.objects.create(user=query.user,teacher=query.teacher,status="pending")
                query.consultant=consult
                data=json.loads(query.user_data)
                data_date=data["date"]
                date=datetime.strptime(data_date,'%m/%d/%Y')
                consult.date=date 
                consult.user_data=json.dumps(data)
                consult.start_time=query.teacher.start_time
                consult.end_time=query.teacher.end_time
                consult.save()
                query.save()
                for i in Cosultant_Payment.objects.filter(user=query.user,teacher=query.teacher,expired=False).exclude(id=query.id).select_related("user"):
                    i.expired=True
                    i.save()
                send_mail(
                    'Payment Completed',
                    f"Successfull Payment of consultant with user {query.user.first_name}",
                    PAYMENT_EMAIL_USERNAME,
                    [query.user.email,consult.teacher.user.email,FINANCE_EMAIL_USERNAME],
                    fail_silently=False,
                    connection=PAYMENT_MAIL_CONNECTION
                    )
                messages.success(request,"Payment Approved Successfully")
            if qs == "course":
                query=get_object_or_404(Course,id=id,status="pending")
                query.status="approved"
                query.save()
                if query.domain_type == 2:
                    change_cache_value(request,name="courses",data_check=query,action="add",number=5,domain="kemet")
                else:
                    change_cache_value(request,name="courses",data_check=query,action="add",number=5)
                messages.success(request,"Course Approved Successfully")
            if qs == "events":   
                query=get_object_or_404(Events,id=id,status="pending")
                query.status="approved"
                query.save()
                change_cache_value(request,name="events",data_check=query,action="add",number=5)
                messages.success(request,"Event Approved Successfully")
                send_mail(
                f'Event {query.name.title()}',
                f"Event {query.name.title()} Approved Successfully",
                DASHBOARD_EMAIL_USERNAME,
                [query.user.email],
                fail_silently=False,
                connection=DASHBOARD_MAIL_CONNECTION
                )
            if qs == "payment":
                query=get_object_or_404(Payment,id=id,status="pending")
                query.created_at= today_datetime.date.today()
                if query.course.domain_type == 1:
                    query.add_expire_time()
                if query.course.domain_type == 2:
                    query.add_expire_time_for_kemet()
                query.status="approved"
                query.course.students.add(query.user)
                if query.course.videos.first():
                    query.course.videos.first().watched_users.add(query.user)
                    query.course.videos.first().save()
                query.course.save()
                query.save()
                for i in Payment.objects.filter(user=query.user,course=query.course,expired=False).exclude(id=query.id).select_related("user"):
                    i.expired=True
                    i.save()
                send_mail(
                'Payment Completed',
                f"Successfull Payment for course {query.course.name} , user {query.user.first_name}",
                PAYMENT_EMAIL_USERNAME,
                [query.user.email,query.course.Instructor.email,FINANCE_EMAIL_USERNAME],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
                messages.success(request,"Payment Approved Successfully")
            if qs == "teacher":
                query=get_object_or_404(TeacherForms,id=id,status="pending")
                query.status="approved"
                query.teacher.account_type="teacher"
                query.teacher.my_data=query.data
                query.teacher.save()
                query.save()
                messages.success(request,"Teacher Approved Successfully")
            if qs == "add_user":
                query = get_object_or_404(AddStudentCourse,id=id,status="pending")
                payment=Payment.objects.create(user=query.student,method="Western Union",transaction_number=f"added-student-{query.student}-{query.id}",
                                                amount=0,course=query.course,
                    status="approved")
                if query.course.domain_type == 1:
                    payment.add_expire_time()
                else:
                    payment.add_expire_time_for_kemet()
                query.course.videos.first().save()
                query.course.save()
                query.status="approved"
                query.course.students.add(query.student)
                query.course.save()
                query.save()
                send_mail(
                f'Course {query.course.name}',
                f"you have been added to course {query.course.name}",
                PAYMENT_EMAIL_USERNAME,
                [query.student.email],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
                messages.success(request,"User Added Successfully")
            if qs == "movies":
                query=get_object_or_404(Movies,id=id,status="pending")
                query.status="approved"
                messages.success(request,"Movie Approved Successfully")
                query.save()
            if qs == "movie_payment":
                query=get_object_or_404(Library_Payment,library_type=3,id=id,status="pending")
                query.status="approved"
                query.get_movies().buyers.add(query.user)
                query.get_movies().save()
                messages.success(request,"Payment Approved Successfully")
                query.save()
                for i in Library_Payment.objects.filter(user=query.user,library_type=3,content_id=query.get_movies().id,expired=False).exclude(id=query.id).select_related("user"):
                    i.expired=True
                    i.save()
                send_mail(
                'Payment Completed',
                "Successfull Payment",
                PAYMENT_EMAIL_USERNAME,
                [query.user.email,FINANCE_EMAIL_USERNAME],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
            if qs == "audios":
                query=get_object_or_404(Audio_Tracks,id=id,status="pending")
                query.status="approved"
                messages.success(request,"Audio Approved Successfully")
                query.save()
            if qs == "audio_book":
                query=get_object_or_404(Audio_Book_Tracks,id=id,status="pending")
                query.status="approved"
                messages.success(request,"Audio Book Approved Successfully")
                query.save()
            if qs == "e_book":
                query=get_object_or_404(E_Book,id=id,status="pending")
                query.status="approved"
                messages.success(request,"E-Book Approved Successfully")
                query.save()
            if qs == "audio_payment":
                query=get_object_or_404(Library_Payment,library_type=2,id=id,status="pending")
                query.status="approved"
                query.get_music().buyers.add(query.user)
                query.get_music().save()
                messages.success(request,"Payment Approved Successfully")
                query.save()
                for i in Library_Payment.objects,filter(user=query.user,library_type=2,content_id=query.get_music().id,expired=False).exclude(id=query.id).select_related("user"):
                    i.expired=True
                    i.save()
                send_mail(
                'Payment Completed',
                "Successfull Payment",
                PAYMENT_EMAIL_USERNAME,
                [query.user.email,FINANCE_EMAIL_USERNAME],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
            if qs == "audio_book_payment":
                query=get_object_or_404(Library_Payment,library_type=1,id=id,status="pending")
                query.status="approved"
                query.get_audio_book().buyers.add(query.user)
                query.get_audio_book().save()
                messages.success(request,"Payment Approved Successfully")
                query.save()
                for i in Library_Payment.objects.filter(user=query.user,content_id=query.get_audio_book().id,library_type=1,expired=False).exclude(id=query.id).select_related("user"):
                    i.expired=True
                    i.save()
                send_mail(
                'Payment Completed',
                "Successfull Payment",
                PAYMENT_EMAIL_USERNAME,
                [query.user.email,FINANCE_EMAIL_USERNAME],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
            if qs == "e_book_payment":
                query=get_object_or_404(Library_Payment,library_type=4,id=id,status="pending")
                query.status="approved"
                query.get_e_book().buyers.add(query.user)
                query.get_e_book().save()
                messages.success(request,"Payment Approved Successfully")
                query.save()
                for i in Library_Payment.objects.filter(user=query.user,library_type=4,content_id=query.get_e_book().id,expired=False).exclude(id=query.id).select_related("user"):
                    i.expired=True
                    i.save()
                send_mail(
                'Payment Completed',
                "Successfull Payment",
                PAYMENT_EMAIL_USERNAME,
                [query.user.email,FINANCE_EMAIL_USERNAME],
                fail_silently=False,
                connection=PAYMENT_MAIL_CONNECTION
                )
        except: 
            return redirect(reverse("dashboard:home"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("home:home"))
    redirect_url = reverse('dashboard:approve')

    # parameters = urlencode()
    return redirect(f'{redirect_url}?approve={qs}') 

@login_required(login_url="accounts:login")
@for_admin_only
def reject(request,id):
    if request.user.is_superuser:
        try:
            qs=request.GET["reject"]
            if qs == "blogs":
                query=get_object_or_404(Blog,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "blog_payment":
                query=get_object_or_404(Blog_Payment,id=id,status="pending")
                content_user=query.user
                mail=PAYMENT_EMAIL_USERNAME
                connection=PAYMENT_MAIL_CONNECTION
            if qs == "consultant_payment":
                query=get_object_or_404(Cosultant_Payment,id=id,status="pending")
                content_user=query.user
                mail=PAYMENT_EMAIL_USERNAME
                connection=PAYMENT_MAIL_CONNECTION
            if qs == "course":
                query=get_object_or_404(Course,id=id,status="pending")
                content_user=query.Instructor
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "events":
                query=get_object_or_404(Events,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "payment":
                query=get_object_or_404(Payment,id=id,status="pending")
                content_user=query.user
                mail=PAYMENT_EMAIL_USERNAME
                connection=PAYMENT_MAIL_CONNECTION
            if qs == "teacher":
                query=get_object_or_404(TeacherForms,id=id,status="pending")
                content_user=query.teacher
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "add_user":
                query=get_object_or_404(AddStudentCourse,id=id,status="pending")
                content_user=query.student
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "movies":
                query=get_object_or_404(Movies,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "movie_payment":
                query=get_object_or_404(Library_Payment,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "audios":
                query=get_object_or_404(Audio_Tracks,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "audio_book":
                query=get_object_or_404(Audio_Book_Tracks,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "e_book":
                query=get_object_or_404(E_Book,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "audio_payment":
                query=get_object_or_404(Library_Payment,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "audio_book_payment":
                query=get_object_or_404(Library_Payment,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            if qs == "e_book_payment":
                query=get_object_or_404(Library_Payment,id=id,status="pending")
                content_user=query.user
                mail=DASHBOARD_EMAIL_USERNAME
                connection=DASHBOARD_MAIL_CONNECTION
            form=RejectForm(request.POST or None)
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.type=qs
                    instance.user=content_user
                    instance.content_id=id
                    instance.save()  
                    send_mail(
                        form.cleaned_data.get("subject"),
                        form.cleaned_data.get("message"),
                        mail,
                        [content_user.email],
                        fail_silently=False,
                        connection=connection
                        )
                 
                    query.status="declined"
                    query.save()
                    messages.success(request,"Content Rejected Successfully")
                    redirect_url = reverse('dashboard:approve')
                    return redirect(f'{redirect_url}?approve={qs}') 
        except:
            return redirect(reverse("dashboard:home"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("home:home"))
    context={"form":form,"query":query,"qs":qs}
    return render(request,"dashboard_reject_form.html",context)

@login_required(login_url="accounts:login")
@admin_director_check
def news(request):
    news=News.objects.all().order_by("-id")
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"news":page_obj}
    return render(request,"dashboard_news.html",context)

@login_required(login_url="accounts:login")
@admin_director_check
def delete_news(request,id):
    news=get_object_or_404(News,id=id)
    news.delete()
    messages.success(request,"News Deleted Successfully")
    return redirect(reverse("dashboard:news"))

@login_required(login_url="accounts:login")
@admin_director_check
def edit_news(request,id):
    news=get_object_or_404(News,id=id)
    form=NewsForm(request.POST or None,instance=news)
    if request.method == "POST":
        instance=form.save(commit=False)
        instance.save()
        messages.success(request,"News Edited Successfully")
        return redirect(reverse("dashboard:news"))
    context={"form":form}
    return render(request,"dashboard_edit_news.html",context)

@login_required(login_url="accounts:login")
@admin_director_check
def add_news(request):
    form=NewsForm(request.POST or None)
    if request.method == "POST":
        instance=form.save(commit=False)
        instance.save()
        messages.success(request,"News Added Successfully")
        return redirect(reverse("dashboard:news"))
    context={"form":form}
    return render(request,"dashboard_add_news.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def consultants(request):
    if request.user.account_type == "teacher" and request.user.is_director == False and request.user.is_superuser == False:
        consultants=Consultant.objects.filter(user=request.user,status="approved").order_by("-id")
    else:
        consultants=Consultant.objects.all().order_by("-id")
    paginator = Paginator(consultants, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"consultants":consultants}
    return render(request,"dashboard_consultants.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def consultants_sessions(request):
    if request.user.account_type == "teacher" and request.user.is_director == False and request.user.is_superuser == False:
        sessions=Teacher_Time.objects.filter(user=request.user,available=True).order_by("-id")
    else:
        sessions=Teacher_Time.objects.all().order_by("-id")

    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"sessions":sessions}
    return render(request,"dashboard_consultants_sessions.html",context)

@login_required(login_url="accounts:login")
def accept_consultant(request,id):
    translation.deactivate()
    consultant=get_object_or_404(Consultant,id=id,status="pending",teacher__user=request.user)
    form=SessionForm(request.POST or None,instance=consultant)
    if request.method =="POST":
        if form.is_valid():
            instance=form.save(commit=False)
            start=request.POST.get("start_time")
            end=request.POST.get("end_time")
            start_time=datetime.strptime(f"{start}","%I:%M:%S %p").time()
            end_time=datetime.strptime(f"{end}","%I:%M:%S %p").time()
            instance.start_time=start_time
            instance.end_time=end_time
            instance.status="approved"
            instance.save()
            body=f"new session with teacher {consultant.teacher.user.first_name} will start on {consultant.date} from {start_time} to {end_time},user {consultant.user.first_name}"
            send_mail(
                "New Session Details",
                body,
                DASHBOARD_EMAIL_USERNAME,
                [consultant.user.email,consultant.teacher.user.email],
                fail_silently=False,
                connection=DASHBOARD_MAIL_CONNECTION
                )
            messages.success(request,"Session Activated")
            return redirect(reverse("dashboard:consultants"))
    context={"form":form}
    return render(request,"dashboard_consultant_accept.html",context)

@login_required(login_url="accounts:login")
def reject_consultant(request,id):
    consultant=get_object_or_404(Consultant,id=id,status="pending",user=request.user)
    consultant.status ="declined"
    payment=Cosultant_Payment.objects.get(consultant=consultant)
    if payment.method != "Western Union":
        refund=Refunds.objects.create(type="consultant_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,)
        data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":payment.get_consultant_date(),"teacher":payment.teacher.user.username}]}
        refund.data=json.dumps(data)
        refund.save()
    payment.expired=True 
    consultant.save()
    send_mail(
        "Consultant Cancellation",
        f"Consultant Has been canceled with teacher {consultant.teacher.user.first_name}",
        DASHBOARD_EMAIL_USERNAME,
        [consultant.user.email,consultant.teacher.user.email],
        fail_silently=False,
        connection=DASHBOARD_MAIL_CONNECTION
        )
    messages.success(request,"Consultant Rejected Successfully")
    return redirect(reverse("dashboard:consultants"))

@login_required(login_url="accounts:login")
def edit_consultant(request,id):
    translation.deactivate()
    consultant=get_object_or_404(Consultant,id=id,status="approved",teacher__user=request.user)
    form=SessionForm(request.POST or None,instance=consultant)
    if request.method =="POST":
        if form.is_valid():
            instance=form.save(commit=False)
            start=request.POST.get("start_time")
            end=request.POST.get("end_time")
            start_time=datetime.strptime(f"{start}","%I:%M:%S %p").time()
            end_time=datetime.strptime(f"{end}","%I:%M:%S %p").time()
            instance.start_time=start_time
            instance.end_time=end_time
            instance.save()
            messages.success(request,"Session Edited Activated")
            send_mail(
            "Consultant Edited",
            f"Consultant Has been edited with teacher {consultant.teacher.user.first_name}",
            DASHBOARD_EMAIL_USERNAME,
            [consultant.user.email,consultant.teacher.user.email],
            fail_silently=False,
            connection=DASHBOARD_MAIL_CONNECTION
            )
            return redirect(reverse("dashboard:consultants"))
    context={"form":form}
    return render(request,"dashboard_consultant_accept.html",context)

@login_required(login_url="accounts:login")
def start_consultant(request,id):
    translation.deactivate()
    consultant=get_object_or_404(Consultant,id=id,status="approved",teacher__user=request.user)
    start_time_day=consultant.date
    start_time=consultant.start_time.strftime("%I:%M:%S %p") 
    end_time=consultant.end_time.strftime("%I:%M:%S %p") 
    body=f"your session will start on {start_time_day} from {start_time} to {end_time}"
    send_mail(
            "session details",
            body,
            DASHBOARD_EMAIL_USERNAME,
            [consultant.user.email],
            fail_silently=False,
            connection=DASHBOARD_MAIL_CONNECTION
            )
    consultant.status="started"
    consultant.save()

    messages.success(request,"consultant started")
    return redirect(reverse("dashboard:consultants"))

@login_required(login_url="accounts:login")
def delete_session(request,id):
    session=get_object_or_404(Teacher_Time,user=request.user,id=id,available=True)
    consult=Consultant.objects.filter(teacher=session).exclude(Q(status="completed") | Q(status="refund"))
    pending_payments=Cosultant_Payment.objects.filter(teacher=session).exclude(Q(status="completed") | Q(status="refund"))
    if pending_payments.exists():
        messages.error(request,"contact the admin , you already have a pending payment")
        return redirect(reverse("dashboard:consultants_sessions"))
    elif consult.exists():
        messages.error(request,"you should complete all pending sessions first")
        return redirect(reverse("dashboard:consultants_sessions"))
    else:
        session.available=False
        session.save()
        teachers=cache.get("teacher_time")
        if teachers: 
            if session in teachers:    
                teachers.remove(session)
                cache.set("teacher_time",teachers,60*30)
        days=cache.get(f"consultant_data_{session.user}")
        if days:
            cache.delete(f"consultant_data_{session.user}")
        messages.success(request,"Session Deactivated")
        return redirect(reverse("dashboard:consultants_sessions"))

@login_required(login_url="accounts:login")
def active_session(request,id):
    session=get_object_or_404(Teacher_Time,user=request.user,id=id,available=False)
    session.available=True
    session.save()
    teachers=cache.get("teacher_time")
    if teachers or teachers == []:
        teachers.append(session)
        cache.set("teacher_time",teachers,60*30) 
    days=cache.get(f"consultant_data_{session.user}")
    if days:
        cache.delete(f"consultant_data_{session.user}")
    messages.success(request,"Session Activated")
    return redirect(reverse("dashboard:consultants_sessions"))
@login_required(login_url="accounts:login")
@check_user_validation 
# @check_if_teacher_have_consultants
def add_consultant(request):  
    translation.deactivate()
    form=CosultantAddForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.user=request.user
            start=request.POST.get("start_time")
            end=request.POST.get("end_time")
            instance.start_time=datetime.strptime(f"{start}","%I:%M:%S %p").time()
            instance.end_time=datetime.strptime(f"{end}","%I:%M:%S %p").time()
            instance.save()
            days=cache.get(f"consultant_data_{instance.user}")
            if days:
                cache.delete(f"consultant_data_{instance.user}")
            messages.success(request,"Consultant Added Successfully")
            return redirect(reverse("dashboard:consultants_sessions"))
    context={"form":form}
    return render(request,"dashboard_add_consultant.html",context)

@login_required(login_url="accounts:login")
@admin_director_check
def add_consultant_category(request):
    form=ConsultantCategoryForm(request.POST or None)
    if request.method == "POST":
        form.save()
        messages.success(request,"Consultant Category Added Successfully")
        form=ConsultantCategoryForm()
    context={"form":form}
    return render(request,"dashboard_add_consultant_category.html",context)
@login_required(login_url="accounts:login")
@check_user_validation
def complete_consultant(request,id):
    consult=get_object_or_404(Consultant,id=id,status="started")
    if request.user == consult.teacher.user:
        consult.status="completed"
        consult.get_consult_payment().expired=True
        consult.get_consult_payment().save()
        consult.save()
        messages.success(request,"Consultant Completed Successfully")
    return redirect(reverse("dashboard:consultants"))

@login_required(login_url="accounts:login")
@admin_director_check
def prices(request):
    prices=Prices.objects.all().order_by("-id")
    context={"prices":prices}
    return render(request,"dashboard_prices.html",context)


@login_required(login_url="accounts:login")
@admin_director_check
def add_price(request):
    form=PriceForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            duration=form.cleaned_data.get("duration")
            data=form.cleaned_data.get("data")
            data={"duration":duration,"details":data}
            instance.data=json.dumps(data)
            instance.save()
            messages.success(request,"price added successfully")
            return redirect(reverse("dashboard:prices"))
    context={"form":form}
    return render(request,"dashboard_add_price.html",context)



@login_required(login_url="accounts:login")
@admin_director_check
def edit_price(request,id):
    price=get_object_or_404(Prices,id=id)
    if request.user.is_superuser:
        prices=get_object_or_404(Prices,id=id)
        form=PriceForm(request.POST or None,instance=price)
        form.initial["data"]=prices.get_details()
        form.initial["duration"]=prices.get_duration()
        if request.method =="POST":
            if form.is_valid():
                instance=form.save(commit=False)
                data=form.cleaned_data.get("data")
                duration=form.cleaned_data.get("duration")
                price_data={"duration":duration,"details":data}
                instance.data=json.dumps(price_data)
                form.save() 
                messages.success(request,"price changed")
                return redirect(reverse("dashboard:prices"))
    else:
        messages.error(request,"you dont't have permission")
        return redirect(reverse("dashboard:home"))
    context={"form":form}
    return render(request,"dashboard_edit_prices.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def add_student_course(request):
    form=AddUserToCourseForm(request.POST or None)
    if request.method =="POST":
        if form.is_valid():
            user=request.POST.get("student")
            course=request.POST.get("course")
            teacher_course=get_object_or_404(Course,Instructor=request.user,id=course,status="approved")
            student_course=get_object_or_404(User,username=user)
            if student_course in teacher_course.students.all():
                messages.error(request,"user is already in course")
            elif AddStudentCourse.objects.filter(course=teacher_course,student=student_course,status="pending").exists():
                messages.error(request,"you already have a pending request for this user")
                # return redirect(reverse("dashboard:"))
            
            elif Payment.objects.filter(user=student_course,course=teacher_course,status="pending").exists():
                messages.error(request,f"you already have a pending payment for user {user} for this course")
            else:
                AddStudentCourse.objects.create(teacher=request.user,student=student_course,course=teacher_course,status="pending")
                body=f"a new student asks to join course {teacher_course.name} by teacher {teacher_course.Instructor.username}"
                subject="new student course"
                send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                messages.success(request,"your request is being processed by admins")
                # return redirect(reverse())
    context={"form":form}
    return render(request,"dashboard_add_user_to_course.html",context)

@login_required(login_url="accounts:login")
@for_admin_only
def add_user_director(request):
    form=AddUserDirector(request.POST or None)
    directors=User.objects.filter(is_director=True,account_type="teacher")
    if request.method =="POST":
        if form.is_valid(): 
            user=request.POST.get("user")
            this_user=User.objects.filter(Q(username=user,account_type="teacher") | Q(email=user,account_type="teacher"))
            if this_user.exists():
                user=this_user.last() 
                if user.is_director:
                    messages.error(request,"this user is already a director ")
                else:
                    user.is_director =True
                    user.save()
                    messages.success(request,"user added successfully")
                    form=AddUserDirector()

    context={"form":form,"directors":directors}
    return render(request,"dashboard_add_user_director.html",context)


import requests
from django.http import JsonResponse
def test(request):
    send_mail_approve(request,user=request.user.email,body="test",subject="test")
    return render(request,"dashboard_test.html")

@login_required(login_url="accounts:login")
@admin_director_check
def add_category(request):
    form=CategoryForm(request.POST or None,request.FILES  or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            file=form.cleaned_data.get("image")
            headers = {
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
            url=f"https://storage.bunnycdn.com/{storage_name}/course_category/{instance.slug}/{file}"
            response = requests.put(url,data=file,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    instance.image = f"https://{agartha_cdn}/course_category/{instance.slug}/{file}"
                    instance.save()
            except:
                pass
            form.save()
            messages.success(request,"category added successfully")
            return redirect(reverse("dashboard:list_category")+"?category=Course")
    context={"form":form}
    return render(request,"dashboard_add_category.html",context)
def list_category(request):
    try:
        qs=request.GET["category"]
        if qs == "Course":
            category=Category.objects.order_by("-id")
        elif qs == "Consultant":
            category=Consultant_Category.objects.order_by("-id")
        elif qs == "Blog":
            category=Blog_Category.objects.order_by("-id")
        else:
            return redirect(reverse("dashboard:home"))
        paginator = Paginator(category, 10) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context={"categories":page_obj,"qs":qs}
    except:
        return redirect(reverse("dashboard:home"))
    return render(request,"dashboard_all_category.html",context)

@login_required(login_url="accounts:login")
@admin_director_check
def add_branch(request):
    form=BranchForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            form=BranchForm()
            messages.success(request,"branch added successfully")
    context={"form":form}
    return render(request,"dashboard_add_branch.html",context)
@login_required(login_url="accounts:login")
@admin_director_check   
def add_blog_category(request):
    form=BlogForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,"blog category added successfully")
            form=BlogForm()
    context={"form":form}
    return render(request,"dashboard_add_blog_category.html",context)

@login_required(login_url="accounts:login")
@admin_director_check   
def terms(request):     #terms edit
    terms=Terms.objects.last()
    form=TermsForm(request.POST or None,instance=terms)
    if request.method == "POST":
        if form.is_valid():
            form.save()
    context={"terms":terms,"form":form}
    return render(request,"dashboard_terms.html",context)

@login_required(login_url="accounts:login")
@admin_director_check   
def terms_add_new(request):     #terms edit
    form=TermsForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
    context={"terms":terms,"form":form}
    return render(request,"dashboard_terms_add_new.html",context)


@login_required(login_url="accounts:login")
@admin_director_check   
def privacy(request):     #terms edit
    terms=Privacy.objects.last()
    form=PrivacyForm(request.POST or None,instance=terms)
    if request.method == "POST":
        if form.is_valid():
            form.save()
    context={"privacy":privacy,"form":form}
    return render(request,"dashboard_privacy.html",context)

@login_required(login_url="accounts:login")
@admin_director_check   
def privacy_add_new(request):     #terms edit
    form=PrivacyForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
    context={"privacy":privacy,"form":form}
    return render(request,"dashboard_privacy_add_new.html",context)


@login_required(login_url="accounts:login")
@admin_director_check  
def emails(request):
    emails=Support_Email.objects.all().order_by("status")
    paginator = Paginator(emails, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"emails":page_obj}
    return render(request,"dashboard_emails.html",context)

@login_required(login_url="accounts:login")
@admin_director_check  
def single_email(request,id):
    try:
        get_email = request.GET["email"]
    except:
       get_email=False
    email=get_object_or_404(Support_Email,id=id)
    if email.status == "solved":
        messages.error(request,"email stauts has been closed")
        return redirect(reverse("dashboard:emails"))

    form = Support_Email_Form(request.POST or None)
    if email.user:
        user_email=email.user.email
    else:
        user_email=email.email
    if request.method == "POST":
        if form.is_valid():
            send_mail(
                form.cleaned_data.get("subject"),
                form.cleaned_data.get("message"),
                SUPPORT_EMAIL_USERNAME,
                [user_email],
                fail_silently=False,
                connection=SUPPORT_MAIL_CONNECTION
                )
            email.status='on process'
            email.save()
            messages.success(request,"mail sent successfully")
            return redirect(reverse("dashboard:emails"))
    context={"email":email,"form":form,"get_email":get_email}
    return render(request,"dashboard_single_email.html",context)


@login_required(login_url="accounts:login")
@admin_director_check  
def close_email(request,id):
    email=get_object_or_404(Support_Email,id=id)
    if email.status != "solved":
        email.status ="solved"
        email.save()
        messages.success(request,'ُEmail status updated')
    else:
        messages.error(request,"email stauts has been closed")
        return redirect(reverse("dashboard:emails"))
    return redirect(reverse("dashboard:emails"))

@login_required(login_url="accounts:login")
@admin_director_check  
def certifications(request):
    certifications=Certification.objects.filter(status='pending').order_by('-id')
    paginator = Paginator(certifications, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={'certifications':page_obj}
    return render(request,"dashboard_certifications.html",context)


@login_required(login_url="accounts:login")
@admin_director_check  
def edit_certifications(request,id):
    certification=get_object_or_404(Certification,id=id,status="pending")
    form=Update_Certification(request.POST or None,request.FILES or None,instance=certification)
    if request.method =="POST":
        if form.is_valid():
            instance=form.save(commit=False)
            file=form.cleaned_data.get("image")
            headers = {
                    "Accept": "*/*", 
                "AccessKey":Storage_Api}
            url=f"https://storage.bunnycdn.com/{storage_name}/certifications/{certification.user.username}/{file}"
            response = requests.put(url,data=file,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    instance.image = f"https://{agartha_cdn}/certifications/{certification.user.username}/{file}"
                    instance.status="received"
                    instance.save()
                    send_mail(
                        "Course Certification",
                        f"your certification image {certification.image}",
                        DASHBOARD_EMAIL_USERNAME,
                        [certification.user.email],
                        fail_silently=False,
                        connection=DASHBOARD_MAIL_CONNECTION
                        )
                 
                    messages.success(request,"Certification Sent Successfully")
                    return redirect(reverse("dashboard:certifications"))
            except:
                messages.error(request,"issue with sending certification")
                pass
    context={'certification':certification,"form":form}
    return render(request,"dashboard_edit_certification.html",context)

@login_required(login_url="accounts:login")
@for_admin_only  
def refunds(request):
    try:
        type = request.GET["type"]
        if type == "blog":
            refunds=Refunds.objects.filter(type="blog_payment").order_by("-id")
        elif type == "course":
            refunds=Refunds.objects.filter(type="course_payment").order_by("-id")
        elif type == "consultant":
            refunds=Refunds.objects.filter(type="consultant_payment").order_by("-id")
        elif type == "movies":
            refunds=Refunds.objects.filter(type="movie_payment").order_by("-id")
        elif type == "music": 
            refunds=Refunds.objects.filter(type="music_payment").order_by("-id")
        elif type == "audio_book": 
            refunds=Refunds.objects.filter(type="audio_book_payment").order_by("-id")
        else:
            return redirect(reverse("dashboard:home"))
    except:
        return redirect(reverse("dashboard:home"))
    paginator = Paginator(refunds, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"refunds":page_obj}
    return render(request,"dashboard_refunds.html",context)

@login_required(login_url="accounts:login")
@for_admin_only  
def search_refunds(request):
    form=Refunds_Form(request.POST or None)
    payment=None
    context={"form":form,"payment":payment}
    if request.method =="POST":
        if form.is_valid():
            instance=form.save(commit=False)
            type=form.cleaned_data.get("type")
            context["type"]=type
            transaction=form.cleaned_data.get("transaction_number")
            if type =="course_payment":
                payment=Payment.objects.filter(transaction_number=transaction).exclude(status="refund")
                context['payment'] = payment
                if payment.exists():
                    messages.success(request,"Course Payment")
                else:
                    messages.error(request,"invalid Course Payment")
            elif type == "blog_payment":
                payment=Blog_Payment.objects.filter(transaction_number=transaction).exclude(status="refund")
                context['payment'] = payment
                if payment.exists():
                    messages.success(request,"Blog Payment")
                else:
                    messages.error(request,"invalid Blog Payment")
            elif type == "consultant_payment":
                payment=Cosultant_Payment.objects.filter(transaction_number=transaction).exclude(status="refund")
                context['payment'] = payment
                if payment.exists():
                    messages.success(request,"Consultant Payment")
                else:
                    messages.error(request,"invalid Consultant Payment")
            elif type == "movie_payment":
                payment=Library_Payment.objects.filter(transaction_number=transaction,library_type=3).exclude(status="refund")
                context['payment'] = payment
                if payment.exists():
                    messages.success(request,"Movies Payment")
                else:
                    messages.error(request,"invalid Movie Payment")
            elif type == "music_payment":
                payment=Library_Payment.objects.filter(transaction_number=transaction,library_type=2).exclude(status="refund")
                context['payment'] = payment
                if payment.exists():
                    messages.success(request,"Music Payment")
                else:
                    messages.error(request,"invalid Music Payment")
    return render(request,"dashboard_add_refund.html",context)


@login_required(login_url="accounts:login")
@for_admin_only 
def add_refund(request,id):
    try:
        type=request.GET["type"]
        if type =="consultant_payment":
            payment=Cosultant_Payment.objects.get(id=id)
            if payment.status != "refund":
                if payment.consultant:
                    payment.consultant.status="refund"
                    payment.consultant.save()
                payment.status ="refund"
                payment.expired=True
                payment.save()
                refund=Refunds.objects.create(type="consultant_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,status="approved")
                data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":payment.get_consultant_date(),"teacher":payment.teacher.user.username}]}
                refund.data=json.dumps(data)
                refund.save()
                messages.success(request,"Payment Refunded")

        elif type == "course_payment":
            payment=Payment.objects.get(id=id)
            if payment.status != "refund": 
                payment.status ="refund"
                try:
                    payment.course.students.remove(payment.user)
                    for i in payment.course.videos.all():
                        i.watched_users.remove(payment.user)
                        i.save()
                    payment.course.save()
                except:
                    pass
                payment.expired=True
                payment.save()
                refund=Refunds.objects.create(type="course_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,status="approved")
                my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","course":payment.course.name}]}
                refund.data=json.dumps(my_data)
                refund.save()
                messages.success(request,"Payment Refunded")
                send_mail(
                    'Payment Refunded',
                    f"Successfull Payment Refund for course {payment.course.name.title},user {payment.user.first_name}",
                    PAYMENT_EMAIL_USERNAME,
                    [payment.user.email,payment.course.Instructor.email],
                    fail_silently=False,
                    connection=PAYMENT_MAIL_CONNECTION
                    )
        elif type == "blog_payment":
            payment=Blog_Payment.objects.get(id=id)
            if payment.status != "refund": 
                payment.status ="refund"
                payment.expired=True
                payment.user.vip=False
                payment.user.save()
                payment.save()
                refund=Refunds.objects.create(type="blog_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,status="approved")
                my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}"}]}
                refund.data=json.dumps(my_data)
                refund.save()
                messages.success(request,"Payment Refunded")
        elif type == "movie_payment":
            payment=Library_Payment.objects.get(id=id,library_type=3)
            if payment.status != "refund": 
                payment.status ="refund"
                payment.expired=True
                try:
                    payment.get_movies().buyers.remove(username=payment.user.username)
                    payment.get_movies.save()
                except:
                    pass
                payment.save()
                refund=Refunds.objects.create(type="movie_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,status="approved")
                my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","movie":payment.get_movies().name}]}
                refund.data=json.dumps(my_data)
                refund.save()
                messages.success(request,"Payment Refunded")
        elif type == "music_payment":
            payment=Library_Payment.objects.get(id=id,library_type=3)
            if payment.status != "refund": 
                payment.status ="refund"
                payment.expired=True
                try:
                    payment.get_music().buyers.remove(username=payment.user.username)
                    payment.get_movies.save()
                except:
                    pass
                payment.save()
                refund=Refunds.objects.create(type="music_payment",content_id=payment.id,transaction_number=payment.transaction_number,user=payment.user,status="approved")
                my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","music":payment.get_music().name}]}
                refund.data=json.dumps(my_data)
                refund.save()
                messages.success(request,"Payment Refunded")
    except:
        return redirect(reverse("dashboard:search_refunds"))
    return redirect(reverse("dashboard:search_refunds"))


@login_required(login_url="accounts:login")
@check_user_validation
@check_consultant_refund
def consultant_refund(request,id):   
    payment=get_object_or_404(Cosultant_Payment,id=id)
    refund=Refunds.objects.create(type="consultant_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":payment.get_consultant_date(),"teacher":payment.teacher.user.username}]}
    refund.data=json.dumps(data)
    refund.save()
    body=f"a new refund from user {request.user.email}"
    subject="new refund"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    messages.success(request,"Your Refund is Being Review By Admin")
    return redirect(reverse("dashboard:consultant_payment"))



@login_required(login_url="accounts:login")
@for_admin_only 
def approve_refund(request,id):
    refund=get_object_or_404(Refunds,id=id,status="pending")
    data=refund.get_refund_data()
    payment=data["payment_id"]  
    if refund.type == "consultant_payment":
        my_payment=Cosultant_Payment.objects.get(id=payment)
        if my_payment.consultant:
            my_payment.consultant.status="refund"
            my_payment.consultant.save()
        my_payment.status ="refund"
        my_payment.expired =True
        my_payment.save()
        refund.status="approved"
        refund.save()
        send_mail(
            'Payment Refunded',
            "Successfull Payment Refund",
            PAYMENT_EMAIL_USERNAME,
            [my_payment.user.email,my_payment.teacher.user.email,FINANCE_EMAIL_USERNAME],
            fail_silently=False,
            connection=PAYMENT_MAIL_CONNECTION
            )
        messages.success(request,"Payment Refunded")
    elif refund.type =="course_payment":
        my_payment=Payment.objects.get(id=payment)
        my_payment.status ="refund"
        my_payment.expired =True
        try:
            my_payment.course.students.remove(my_payment.user)
            for i in my_payment.course.videos.all():
                i.watched_users.remove(my_payment.user)
                i.save()
            my_payment.course.save()
        except:
            pass
        my_payment.save()
        refund.status="approved"
        refund.save()
        send_mail(
            'Payment Refunded',
            f"Successfull Payment Refund for course {my_payment.course.name.title},user {my_payment.user.first_name}",
            PAYMENT_EMAIL_USERNAME,
            [my_payment.user.email,my_payment.course.Instructor.email,FINANCE_EMAIL_USERNAME],
            fail_silently=False,
            connection=PAYMENT_MAIL_CONNECTION
            )
        messages.success(request,"Payment Refunded")
    elif refund.type =="movie_payment":
        my_payment=Library_Payment.objects.get(id=payment,library_type=3)
        my_payment.status ="refund"
        my_payment.expired =True

        try:
            my_payment.get_movies().buyers.remove(my_payment.user)
            my_payment.get_movies().save()
        except:
            pass
        my_payment.save()
        refund.status="approved"
        refund.save()
        send_mail(
            'Payment Refunded',
            "Successfull Payment Refund",
            PAYMENT_EMAIL_USERNAME,
            [my_payment.user.email,FINANCE_EMAIL_USERNAME],
            fail_silently=False,
            connection=PAYMENT_MAIL_CONNECTION
            )
        messages.success(request,"Payment Refunded")
    elif refund.type =="music_payment":
        my_payment=Library_Payment.objects.get(id=payment,library_type=2)
        my_payment.status ="refund"
        my_payment.expired =True
        try:
            my_payment.get_music().buyers.remove(my_payment.user)
            my_payment.get_music().save()
        except:
            pass
        my_payment.save()
        refund.status="approved"
        refund.save()
        send_mail(
            'Payment Refunded',
            "Successfull Payment Refund",
            PAYMENT_EMAIL_USERNAME,
            [my_payment.user.email,FINANCE_EMAIL_USERNAME],
            fail_silently=False,
            connection=PAYMENT_MAIL_CONNECTION
            )
        messages.success(request,"Payment Refunded")
    elif refund.type =="audio_book_payment":
        my_payment=Library_Payment.objects.get(id=payment,library_type=1)
        my_payment.status ="refund"
        my_payment.expired =True
        try:
            my_payment.get_audio_book().buyers.remove(my_payment.user)
            my_payment.get_audio_book().save()
        except:
            pass
        my_payment.save()
        refund.status="approved"
        refund.save()
        send_mail(
            'Payment Refunded',
            "Successfull Payment Refund",
            PAYMENT_EMAIL_USERNAME,
            [my_payment.user.email,FINANCE_EMAIL_USERNAME],
            fail_silently=False,
            connection=PAYMENT_MAIL_CONNECTION
            )
        messages.success(request,"Payment Refunded")
    elif refund.type == "e_book_payment":
        my_payment=Library_Payment.objects.get(id=payment,library_type=4)
        my_payment.status ="refund"
        my_payment.expired =True
        try:
            my_payment.get_e_book().buyers.remove(my_payment.user)
            my_payment.get_e_book().save()
        except:
            pass
        my_payment.save()
        refund.status="approved"
        refund.save()
        send_mail(
            'Payment Refunded',
            "Successfull Payment Refund",
            PAYMENT_EMAIL_USERNAME,
            [my_payment.user.email,FINANCE_EMAIL_USERNAME],
            fail_silently=False,
            connection=PAYMENT_MAIL_CONNECTION
            )
        messages.success(request,"Payment Refunded")
    return redirect(reverse("dashboard:search_refunds"))

@login_required(login_url="accounts:login")
@check_user_validation
@check_course_refund
def course_refund(request,slug,id):   
    payment=get_object_or_404(Payment,id=id)
    refund=Refunds.objects.create(type="course_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","course":payment.course.name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    body=f"a new refund from user {request.user.email}"
    subject="new refund"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    messages.success(request,"Your Refund is Being Review By Admin")
    return redirect(reverse("dashboard:course_payment"))
 
@login_required(login_url="accounts:login")
@check_user_validation
@check_edit_blog_pyment
def edit_blog_payment(request,id):
    payment=get_object_or_404(Blog_Payment,id=id,status="declined")
    form=BlogPaymentFom(request.POST or None,request.FILES or None,instance=payment)
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/blog-payment/{instance.user.slug}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/blog-payment/{instance.user.slug}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:blog_payment"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("accounts:blog_payment"))
    context={"form":form}
    return render(request,"dashboard_edit_blog_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
@check_edit_course_pyment
def edit_course_payment(request,id):
    payment=get_object_or_404(Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            form=CoursePaymentFom(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    # today= today_datetime.date.today()
                    instance.expired_at=instance.created_at
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/course-payment/{instance.course.slug}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/course-payment/{instance.course.slug}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:course_payment"))
        else:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:course_payment"))
    context={"form":form,"payment":payment} 
    return render(request,"dashboard_edit_course_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
@check_edit_consultant_pyment
def edit_consultant_payment(request,id):
    payment=get_object_or_404(Cosultant_Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            form=ConsultantPaymentFom(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/consultant-payment/{instance.user.slug}/{instance.consult.teacher.date}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/consultant-payment/{instance.user.slug}/{instance.consult.teacher.date}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:consultant_payment"))
        else:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:consultant_payment"))
    context={"form":form}
    return render(request,"dashboard_edit_consultant_payment.html",context)

########## libraries
@login_required(login_url="accounts:login")
@check_user_validation
def library(request):
 
    # return redirect(reverse("dashboard:home"))
    context={} 
    return render(request,"dashboard_library.html",context)

@login_required(login_url="accounts:login")
@check_user_validation
def add_library_category(request):
    form=LibraryCategoryForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request,"library category added successfully")
        form=LibraryCategoryForm()
    context={"form":form} 
    return render(request,"dashboard_add_library_category.html",context)

def add_images_to_library(request,form,images,url_name):
    status=False
    instance=form.save(commit=False)
    library_data={"images":[]}
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
                instance.save()
        except:
            pass
    instance.data=json.dumps(library_data)
    instance.save()
    messages.success(request,"library added successfully")
    status=True
    return status
# @login_required(login_url="accounts:login")
# @check_user_validation
# def add_e_book(request):
#     form=E_Book_LibraryForm(request.POST or None,request.FILES or None)
#     if request.method == "POST":
#         if form.is_valid():
#             response=add_to_library(request,form,slug="e_book")
#             if response:
#                 return redirect(reverse("dashboard:add_e_book_file"))
#     context={"form":form} 
#     return render(request,"dashboard_add_library.html",context)

# @login_required(login_url="accounts:login")
# @check_user_validation
# def add_e_book_file(request,slug):
#     book=get_object_or_404(E_Book,status="pending")
#     if book.get_book():
#         pass
#     form=E_Book_File_Form(request.POST or None,request.FILES or None)
#     if request.method == "POST":
#         if form.is_valid():
#             response=add_to_library(request,form,slug="e_book")
#             if response:
#                 return redirect(reverse("dashboard:add_e_book_file"))
#     context={"form":form} 
#     return render(request,"dashboard_add_library.html",context)



########## libraries

@login_required(login_url="accounts:login")
@for_admin_only
def ads(request,slug):
    if slug == "agartha":
        ads=Ads.objects.filter(domain_type=1)
    elif slug == "kemet":
        ads=Ads.objects.filter(domain_type=2)
    else:
        return redirect(reverse("dashboard:home"))
    context={"ads":ads} 
    return render(request,"dashboard_ads.html",context)


@login_required(login_url="accounts:login")
@for_admin_only
def search_ads(request):  
    form=AdsForm(request.POST or None)
    course=None
    domain=None
    if request.method == "POST":
        if form.is_valid():
            course=Course.objects.filter(name__icontains=form.cleaned_data.get("course"))
            domain=form.cleaned_data.get("domain")
    context={"form":form,"course":course,"domain":domain} 
    return render(request,"dashboard_add_ads.html",context)


@login_required(login_url="accounts:login")
@for_admin_only
def add_ads(request,id,domain):  
    course=get_object_or_404(Course,id=id)
    if not Ads.objects.filter(course=course,domain_type=domain).exists():
        if int(course.domain_type) == int(domain):
            messages.error(request,"course is already on this domain")
        else:
            ads=Ads.objects.create(course=course,domain_type=domain)
            if int(domain) == 2:
                change_cache_value(request,name="ads",data_check=ads,action="add",domain="kemet")
            else:
                change_cache_value(request,name="ads",data_check=ads,action="add")
            messages.success(request,"course added successfully to the Ads")
    else: 
        messages.error(request,"course is already in Ads")
    return redirect(reverse("dashboard:search_ads"))
@login_required(login_url="accounts:login")
@for_admin_only
def remove_ads(request,id):  
    ads=get_object_or_404(Ads,id=id)
    if ads.domain_type == 2:
        change_cache_value(request,name="ads",data_check=ads,action="remove",domain="kemet")
    else:
        change_cache_value(request,name="ads",data_check=ads,action="remove")
    ads.delete()
    messages.success(request,"Ads deleted successsfully")

    return redirect(reverse("dashboard:ads",kwargs={"slug":ads.get_domain()}))