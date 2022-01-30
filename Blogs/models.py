# Create your models here.
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import random,string
import json

from django.shortcuts import render
from django.conf import settings
from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model
import requests 
User=get_user_model()

import string,random

def converter(self):   
    try:
            api=requests.get("http://api.currencylayer.com/live?access_key=bbd4b1fcbe13b2bf0b8a008bc1daa606&currencies=EGP&format = 1")
            price=api.json()
            for i in price["quotes"]: 
                pass 
            money=price["quotes"][i] * self.price
            total=round(money)
            self.egy_currency=total
            self.save()
            
    except:
        total=None
    return total   
def random_string_generator(size = 5, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
class Category(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Blog_Comment(models.Model):
    blog=models.ForeignKey("Blog",related_name="blog_comment",on_delete=models.CASCADE)
    comment=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.blog.name
    def get_blog_comments_replies(self):
        replies=Blog_Comment_Reply.objects.filter(comment=self)
        return replies       

class Blog_Comment_Reply(models.Model):
    blog=models.ForeignKey("Blog",related_name="blog_comment_reply",on_delete=models.CASCADE)
    comment=models.ForeignKey(Blog_Comment,on_delete=models.CASCADE)
    reply=models.CharField(max_length=200)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.blog.name
def upload_blog_images(instance,filename):
    return (f"blogs/images/{instance.blog.slug}/{filename}")
BLOG_TYPE=(
    ("standard","standard"),
    ("gallery","gallery"),
    ("video","video"),
    ("audio","audio"),
    ("quote","quote"),
    ("link","link"),
                
)  
class Blog_Images(models.Model):
    blog=models.ForeignKey("Blog",on_delete=models.CASCADE,)
    image=models.ImageField(upload_to=upload_blog_images)

    def __str__(self):
        return self.blog.name


        
def upload_blog_videos(instance,filename):
    return (f"blogs/videos/{instance.slug}/{filename}")

BLOG_STATUS=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined")
)
class Blog(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    details=RichTextField()
    data=models.TextField(blank=True)
    image=models.ManyToManyField(Blog_Images,related_name="blog_comment",blank=True)
    video=models.FileField(blank=True,null=True,upload_to=upload_blog_videos,max_length=400)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    paid=models.BooleanField(default=False)
    comments=models.ManyToManyField(Blog_Comment,related_name="blog_comments",blank=True)
    blog_type=models.CharField(choices=BLOG_TYPE,max_length=20)
    status=models.CharField(choices=BLOG_STATUS,max_length=50,default="pending")
    tags=TaggableManager()
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Blog.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
            else:
                self.slug = slugify(self.name)          
        super(Blog, self).save()
    def __str__(self):
        return self.name

    def get_views(self):
        try:
            views=self.blog_viewers.viewers.count()
        except:
            views=0
        return views
    def check_blog_viwers(self,user):
        try:
            if self.blog_viewers.viewers.get(id=user):
                count=self.blog_viewers.viewers.count()
            else:
                self.blog_viewers.viewers.add(id=user)
                self.blog_viewers.viewers.save()
                count=self.blog_viewers.viewers.count()
        except:
            count=0
        return count

    def get_quote(self):
        try:
            data=json.loads(self.data)
            quote=data["quote"]
        except:
            quote=None
        return quote
    def get_link(self):
        try:
            data=json.loads(self.data)
            link=data["link"]
        except:
            link=None
        return link

    def same_category(self):
        blogs=Blog.objects.filter(status="approved",category=self.category).order_by("-created_at")[:5]
        return blogs

    def get_comments(self):
        comments=self.comments.count()
        replies=self.blog_comment_reply.count()
        count=comments + replies
        return count
    def get_blog_video_status(self):
        if self.blog_type =="video" :
            try:
                blog_data=json.loads(self.data)
                length=blog_data["video_length"]
            except:
                length=None
        else:
            length=None
        return length
    def get_blog_audio_status(self):
        if self.blog_type =="audio" and self.video == None :
            audio=True
        else:
            audio =False
        return audio
@receiver(post_save, sender=Blog)
def create_blog_viewers(sender, instance, created, **kwargs):
    if created:
        Blog_Views.objects.create(blog=instance)

def get_blog_data():
    teacher=User.objects.filter(account_type="teacher",is_active=True).order_by("?")[:6]
    cat=Category.objects.order_by("-id")[:6]
    slider_blogs=Blog.objects.filter(status="approved").order_by("-created_at")[:5]
    recent_blog=Blog.objects.filter(status="approved").order_by("-created_at")[:6]
    blogs=Blog.objects.filter(status="approved").order_by("-id")
    context={"recent_teachers":teacher,"recent_categories":cat,"slider":slider_blogs,"recent_blogs":recent_blog,"blogs":blogs}
    return context

def recent_teachers():
    teacher=User.objects.filter(account_type="teacher",is_active=True).order_by("?")[:6]
    return teacher 
def recent_categories():
    cat=Category.objects.order_by("-id")[:6]
    return cat
def blog_slider():
    blogs=Blog.objects.filter(status="approved").order_by("-created_at")[:5]
    return blogs

def recent_blogs():
    blog=Blog.objects.filter(status="approved").order_by("-created_at")[:6]
    return blog

class Blog_Views(models.Model):
    blog=models.OneToOneField(Blog,on_delete=models.CASCADE,related_name="blog_viewers")
    viewers=models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.blog.name

PAYMENTS=(
    ("Paymob","Paymob"),
    ("Western Union","Western Union"),
    ("Paypal","Paypal")
)
def upload_blog_payment(instance,filename):
    return (f"payment/blogs/{instance.user.username}/{filename}")



PAYMENT_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"),
    ("refund","refund"),

    )
class Blog_Payment(models.Model):
    method=models.CharField(choices=PAYMENTS,max_length=50)
    payment_image=models.ImageField(upload_to=upload_blog_payment,blank=True,null=True)
    # phone=models.CharField(null=True,max_length=20)
    transaction_number=models.CharField(max_length=50,null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    created_at=models.DateField()
    expired_at=models.DateField(blank=True,null=True)
    expired=models.BooleanField(default=False)

    def __str__(self):
        return self.method


class Prices(models.Model):
    name=models.CharField(max_length=50)
    price=models.FloatField(default=0)
    data=models.TextField()
    def __str__(self):
        return self.name
    
    def get_duration(self):
        data=json.loads(self.data)
        duration=data["duration"]
        return duration
    def __str__(self):
        return self.name
        
    def get_details(self):
        data=json.loads(self.data)
        details=data["details"]
        return details
