# Create your models here.
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import random,string
import json
from Dashboard.models import Rejects
from django.shortcuts import render
from django.conf import settings
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model
User=get_user_model()

import string,random


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

class CheckRejectManager(models.Manager):
    def get_query_set(self):
        rejects=Rejects.objects.filter(type="blogs")
        list=[]
        for i in rejects:
            # i.content_id
            list.append(i.content_id)
        blogs=Blog.objects.filter(approved=False).exclude(id__in=list)
        return blogs
        
def upload_blog_videos(instance,filename):
    return (f"blogs/videos/{instance.slug}/{filename}")
class Blog(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    details=RichTextUploadingField()
    data=models.TextField(blank=True)
    image=models.ManyToManyField(Blog_Images,related_name="blog_comment",blank=True)
    video=models.FileField(blank=True,null=True,upload_to=upload_blog_videos)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    paid=models.BooleanField(default=False)
    comments=models.ManyToManyField(Blog_Comment,related_name="blog_comments",blank=True)
    blog_type=models.CharField(choices=BLOG_TYPE,max_length=20)
    approved=models.BooleanField(default=False)
    tags=TaggableManager()
    check_reject=CheckRejectManager()   
    objects=models.Manager()
    slug=models.SlugField(unique=True,blank=True,max_length=100)

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
        blogs=Blog.objects.filter(approved=True,category=self.category).order_by("-created_at")[:5]
        return blogs

    def get_comments(self):
        comments=self.comments.count()
        replies=self.blog_comment_reply.count()
        count=comments + replies
        return count
    # def 

@receiver(post_save, sender=Blog)
def create_blog_viewers(sender, instance, created, **kwargs):
    if created:
        Blog_Views.objects.create(blog=instance)

@receiver(pre_save, sender=Blog) 
def pre_save_receiver(sender, instance, *args, **kwargs):       
    if not instance.slug: 

        instance.slug = slugify(instance.name)
        if Blog.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug)
        else:
            slug=f"{instance.name}"
            instance.slug = slugify(slug)

def recent_teachers():
    teacher=User.objects.filter(account_type="teacher",is_active=True).order_by("?")[:6]
    return teacher 
def recent_categories():
    cat=Category.objects.order_by("-id")[:6]
    return cat
def blog_slider():
    blogs=Blog.objects.filter(approved=True).order_by("-created_at")[:5]
    return blogs

def recent_blogs():
    blog=Blog.objects.filter(approved=True).order_by("-created_at")[:6]
    return blog

class Blog_Views(models.Model):
    blog=models.OneToOneField(Blog,on_delete=models.CASCADE,related_name="blog_viewers")
    viewers=models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.blog.name

PAYMENTS=(
    ("Bank Transaction","Bank Transaction"),
    ("Western Union","Western Union"),
    ("Vodafone Cash","Vodafone Cash"),
    ("Paypal","Paypal")
)
def upload_blog_payment(instance,filename):
    return (f"payment/blogs/{instance.user.username}/{filename}")

class CheckRejectBlogPaymentManager(models.Manager):
    def get_query_set(self):
        rejects=Rejects.objects.filter(type="blog_payment")
        list=[]
        for i in rejects:
            # i.content_id
            list.append(i.content_id)
        payments=Blog_Payment.objects.filter(status="pending").exclude(id__in=list)
        return payments

PAYMENT_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"),

    )
class Blog_Payment(models.Model):
    method=models.CharField(choices=PAYMENTS,max_length=50)
    payment_image=models.ImageField(upload_to=upload_blog_payment,blank=True,null=True)
    # phone=models.CharField(null=True,max_length=20)
    transaction_number=models.CharField(max_length=50,null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    objects=models.Manager()
    check_reject=CheckRejectBlogPaymentManager()
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
