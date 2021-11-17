# Create your models here.
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import random,string
from django.conf import settings
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
User=settings.AUTH_USER_MODEL
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
    return (f"blogs/{instance.blog.slug}/{filename}")
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
class Blog(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    details=RichTextUploadingField()
    data=models.TextField(blank=True)
    image=models.ManyToManyField(Blog_Images,related_name="blog_comment",blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    comments=models.ManyToManyField(Blog_Comment,related_name="blog_comments",blank=True)
    blog_type=models.CharField(choices=BLOG_TYPE,max_length=20)
    approved=models.BooleanField(default=False)
    tags=TaggableManager()
    slug=models.SlugField(unique=True,blank=True)

    def __str__(self):
        return self.name

    def same_category():
        blogs=Blog.objects.filter(approved=True,category=self.category).order_by("-created_at")[:5]
        return blogs

    def get_comments(self):
        comments=self.comments.count()
        replies=self.blog_comment_reply.count()
        print(replies,comments)
        count=comments + replies

        return count

@receiver(post_save, sender=Blog)
def create_blog_viewers(sender, instance, created, **kwargs):
    if created:
        Blog_Views.objects.create(blog=instance)

@receiver(pre_save, sender=Blog) 
def pre_save_receiver(sender, instance, *args, **kwargs):       
    if not instance.slug: 
        print("asd")
        instance.slug = slugify(instance.name)
        if Blog.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug)
        else:
            slug=f"{instance.name}"
            instance.slug = slugify(slug)

                

def blog_slider():
    blogs=Blog.objects.filter(approved=True).order_by("-created_at")[:5]
    return blogs


class Blog_Views(models.Model):
    blog=models.OneToOneField(Blog,on_delete=models.CASCADE,related_name="blog_viewers")
    viewers=models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.blog.name