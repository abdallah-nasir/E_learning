# Create your models here.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import random,string
from django.shortcuts import redirect
from django.urls import reverse
from home import models as Home_Models
import json,datetime
from django.contrib import messages
from Dashboard.models import Rejects
from django.shortcuts import render
from django.conf import settings
from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model
User=get_user_model()
def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")       
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str
import string,random

def random_string_generator(size = 5, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

DOMAIN=(
    (1,"agartha"),
    (2,"kemet"),
)
class Category(models.Model):
    name=models.CharField(max_length=100)
    domain_type=models.IntegerField(choices=DOMAIN,default=1)

    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Category.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Category, self).save()

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
    domain_type=models.IntegerField(choices=DOMAIN,default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    paid=models.BooleanField(default=False)
    comments=models.ManyToManyField(Blog_Comment,related_name="blog_comments",blank=True)
    viewers=models.ManyToManyField(User,related_name="blog_viewers",blank=True)
    blog_type=models.CharField(choices=BLOG_TYPE,max_length=20)
    status=models.CharField(choices=BLOG_STATUS,max_length=50,default="pending")
    tags=TaggableManager()
    slug=models.SlugField(unique=True,blank=True,max_length=100)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Blog.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{self.user.username}"
                if Blog.objects.filter(slug=self.slug).exists():
                    self.slug=f"{slug}-{self.user}-{random_string_generator()}"
            else:
                self.slug = slugify(self.name)          
        super(Blog, self).save()
        
    def get_views(self):
        views=self.viewers.count()
        return views
    def check_blog_viwers(self,user):
        current_user=self.viewers.filter(username=user)
        if not current_user.exists():
            self.viewers.add(user)
            self.save()
        count=self.viewers.count()
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
        blogs=Blog.objects.filter(status="approved",category=self.category,domain_type=1).order_by("-created_at")[:5]
        return blogs
    def same_kemet_category(self):
        blogs=Blog.objects.filter(status="approved",category=self.category,domain_type=2).order_by("-created_at")[:5]
        return blogs
    def get_comments(self):
        comments=self.comments.count()
        replies=self.blog_comment_reply.count()
        count=comments + replies
        return count
    def get_blog_video_status(self):
        if self.blog_type =="video" or self.blog_type =="audio":
            try:
                blog_data=json.loads(self.data)
                length=blog_data["video_length"]
                if length > 0:
                    result =True
                else:
                    result=False
            except:
                result=False
        else:
            result=False
        return result
    def get_blog_audio_status(self):
        if self.blog_type =="audio" :
            if not self.video:
                show=True
            else:
                show=False
        else:
            show=False
        return show
# @receiver(post_save, sender=Blog)
# def create_blog_viewers(sender, instance, created, **kwargs):
#     if created:
#         Blog_Views.objects.create(blog=instance)
from crum import get_current_request   
def check_if_payment_expired(user):
    request=get_current_request()
    today= datetime.date.today()
    payment=Blog_Payment.objects.filter(user=user,expired=False,status="approved").select_related("user").last()
    if payment.expired_at <= today:
        payment.expired=True
        payment.save()
        payment.user.vip =False
        payment.user.save()
        messages.error(request,"your membership has expired")
        result=True
    else:
        result=False
    return result
def get_blog_data():
    teacher=User.objects.filter(account_type="teacher",is_active=True).order_by("?")[:6]
    cat=Category.objects.filter(domain_type=1).order_by("-id")[:6]
    blogs_query=Blog.objects.filter(status="approved",domain_type=1)
    blogs=blogs_query.order_by("-id")
    slider_blogs=blogs_query.order_by("-created_at")[:5]
    recent_blog=blogs_query.order_by("-created_at")[:6]
    context={"recent_teachers":list(teacher),"recent_categories":list(cat),"slider":list(slider_blogs),"recent_blogs":list(recent_blog),"blogs":list(blogs)}
    return context

def get_kemet_blog_data():
    teacher=User.objects.filter(account_type="teacher",is_active=True).order_by("?")[:6]
    cat=Category.objects.filter(domain_type=2).order_by("-id")[:6]
    blogs_query=Blog.objects.filter(status="approved",domain_type=2)
    blogs=blogs_query.order_by("-id")
    slider_blogs=blogs_query.order_by("-created_at")[:5]
    recent_blog=blogs_query.order_by("-created_at")[:6]
    context={"recent_teachers":list(teacher),"recent_categories":list(cat),"slider":list(slider_blogs),"recent_blogs":list(recent_blog),"blogs":list(blogs)}
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
def blog_kemet_slider():
    blogs=Blog.objects.filter(status="approved",domain_type=2).order_by("-created_at")[:5]
    return blogs
   
def recent_blogs():
    blog=Blog.objects.filter(status="approved").order_by("-created_at")[:6]
    return blog
def recent_kemet_blogs():
    blog=Blog.objects.filter(status="approved",domain_type=2).order_by("-created_at")[:6]
    return blog
# class Blog_Views(models.Model):
#     blog=models.OneToOneField(Blog,on_delete=models.CASCADE,related_name="blog_viewers")
#     viewers=models.ManyToManyField(User,blank=True)

#     def __str__(self):
#         return self.blog.name

PAYMENTS=(
    ("bank","bank"),
    ("Western Union","Western Union"),
    ("Paypal","Paypal")
)
def upload_blog_payment(instance,filename):
    return (f"payment/blogs/{instance.user.username}/{filename}")
PRICE_TYPE=(
    (1,"agartha"),
    (2,"kemet")
)


class Prices(models.Model):
    name=models.CharField(max_length=50)
    price=models.FloatField(default=0)
    type=models.IntegerField(choices=PRICE_TYPE,default=1)
    data=RichTextField()
    def __str__(self):
        return self.name
    def get_type(self):
        type=None
        for i in PRICE_TYPE:
            while i[0] == self.type:
                type = PRICE_TYPE[self.type-1][1] 
                break
        return type
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
    amount=models.PositiveIntegerField(default=0)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    data=models.TextField(blank=True,null=True)
    type=models.IntegerField(choices=PRICE_TYPE,default=1)
    created_at=models.DateField()
    expired_at=models.DateField(blank=True,null=True)
    expired=models.BooleanField(default=False)

    def __str__(self):    
        return self.method

    def check_payment(self):
        if self.expired == True:
            return False
        if self.type == 1:
            if self.user.vip == True:
                return False
            else:
                return True
        if self.type == 2:
            if self.user.is_kemet_vip == True:
                return False
            else:
                return False
        if self.status == "declined":
            if self.method == "Western Union" or self.method == "bank":
                return True
            else:
                return False
        else:
            return False
    def check_refund(self): 
        if self.status != "refund":
            if self.method == "Western Union":
                return False
            else:
                return True
        else:
            return False 
    def add_time_expired_to_related_course(self):
        payments=Home_Models.Payment.objects.filter(user=self.user,course__domain_type=1,status="approved",expired=False).select_related("user")
        # today=datetime.date.today()
        # difference=self.expired_at - today
        if payments.exists():
            data=json.loads(self.data)
            duration=data["duration"] 
            if duration == 12:
                time_duration=365
            if duration == 6: 
                time_duration=30*6
            if duration == 3:
                time_duration=30*3
            for i in payments:
                i.expired_at += datetime.timedelta(days=time_duration)
                i.save()
        return True

    def add_time_expired_to_related_course_kemet(self):
        payments=Home_Models.Payment.objects.filter(user=self.user,course__domain_type=2,status="approved",expired=False).select_related("user")
        # today=datetime.date.today()
        # difference=self.expired_at - today
        if payments.exists():
            data=json.loads(self.data)
            duration=data["duration"] 
            if duration == 12:
                time_duration=365
            if duration == 6: 
                time_duration=30*6
            if duration == 3:
                time_duration=30*3
            for i in payments:
                i.expired_at += datetime.timedelta(days=time_duration)
                i.save()
        return True