from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from .manager import *
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import random,string
from django.conf import settings
import json

def random_string_generator(size=7, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Create your models here.
def upload_avatar(instance,filename):
    place=f"avatar/{instance.username}/{filename}"
    return place
ACCOUNT_TYPE=(
    ("student","student"),
    ("teacher","teacher") 
)
class User(AbstractUser):
    account_type=models.CharField(choices=ACCOUNT_TYPE,max_length=20)
    phone=models.CharField(max_length=12)
    image=models.ImageField(upload_to=upload_avatar)
    my_data=models.TextField(blank=True,null=True)
    code=models.CharField(max_length=50,blank=True,null=True)
    slug=models.SlugField(unique=True,blank=True,null=True)
    def __str__(self):
        return self.username

    def get_user_data(self):
        data=json.loads(self.my_data)
        # title=data["title"]
        # social=data["social"]
        about_me=data["about_me"]
        context={"about_me":about_me}
        return context
class LoggedInUser(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE, related_name='logged_in_user')
    session_key = models.CharField(max_length=100, null=True, blank=True)
    
    # def __str__(self):
    #     return self.session_key

@receiver(post_save, sender=User)
def create_user_session(sender, instance, created, **kwargs):
    if created:
        LoggedInUser.objects.create(user=instance)

@receiver(pre_save, sender=User)
def pre_save_receiver_video(sender, instance, *args, **kwargs):
    instance.slug=slugify(instance.username) 
    # if User.objects.filter(slug=instance.slug).exists():
    #     slug=f"{instance.username}-{instance.id}"
    #     instance.slug = slugify(slug) 
    # else:      
    #     slug=f"{instance.username}" 
    #     instance.slug = slugify(slug) 

auth_user=settings.AUTH_USER_MODEL
class TeacherForms(models.Model):
    teacher=models.ForeignKey(auth_user,on_delete=models.CASCADE)
    approved=models.BooleanField(default=False)
    code=models.CharField(max_length=50)
    data=models.TextField()    

    def __str__(self):
        return self.teacher.username

