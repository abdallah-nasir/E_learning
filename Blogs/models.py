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

class Category(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.blog.name
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
    return (f"blogs/{instance.user}/{instance.name}/{filename}")
BLOG_TYPE=(
    ("standard","standard"),
    ("gallery","gallery"),
    ("video","video"),
    ("audio","audio"),
    ("quote","quote"),
    ("link","link"),
            
)  
class Blog(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    details=RichTextUploadingField()
    image=models.ImageField(upload_to=upload_blog_images)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    comments=models.ManyToManyField(Blog_Comment,related_name="blog_comments",blank=True)
    blog_type=models.CharField(choices=BLOG_TYPE,max_length=20)
    approved=models.BooleanField(default=False)
    tags=TaggableManager()

@receiver(post_save, sender=Blog)
def create_blog_viewers(sender, instance, created, **kwargs):
    if created:
        Blog_Views.objects.create(blog=instance)

@receiver(pre_save, sender=Blog) 
def pre_save_receiver(sender, instance, *args, **kwargs):       
    if instance.slug == None: 
        instance.slug = slugify(instance.name)
        if Blog.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug)
        else:
            slug=f"{instance.name}"
            instance.slug = slugify(slug)


class Blog_Views(models.Model):
    blog=models.OneToOneField(Blog,on_delete=models.CASCADE,related_name="blog_viewers")
    viewers=models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.blog.name