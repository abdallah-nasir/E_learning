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
from home import models as home_models
import json,os 
default_image=os.environ["default_image"]
agartha_cdn=os.environ["agartha_cdn"]
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
GENDER=(
    ("male","male"),
    ("female","female")  
)   

class User(AbstractUser):
    account_type=models.CharField(choices=ACCOUNT_TYPE,max_length=20,default="student")
    phone=models.CharField(max_length=12)
    account_image=models.ImageField(blank=True,null=True,default=f"{default_image}")
    gender=models.CharField(max_length=20,choices=GENDER,default="male")
    my_data=models.TextField(blank=True,null=True)
    code=models.CharField(max_length=50,blank=True,null=True)
    slug=models.SlugField(unique=True,blank=True,null=True)
    vip =models.BooleanField(default=False)
    is_director=models.BooleanField(default=False)
    terms_privacy=models.BooleanField(default=True,blank=False)
    def __str__(self):
        return self.username
    def save(self, *args, **kwargs):
        if self.slug == None:
            self.slug = slugify(self.username)
            if User.objects.filter(slug=self.slug).exists():
                slug=slugify(self.username)
                self.slug =f"{slug}-{random_string_generator()}"
            else:
                self.slug = slugify(self.username)          
        super(User, self).save()
        
    def image(self):
        return self.account_image
    def get_user_data(self):
        data=json.loads(self.my_data)
        title=data["title"]
        social=[]
        about_me=data["about_me"]
        for i in data["social"]:      
            if i["facebook"]:
                facebook=i["facebook"]
            else:
                facebook=None
            if i["twitter"]:
                twitter=i["twitter"]
            else:
                twitter=None
            if i["linkedin"]:
                linkedin=i["linkedin"]
            else:
                linkedin=None
        context={"about_me":about_me,"title":title,"facebook":facebook,"linkedin":linkedin,"twitter":twitter}
        return context

    def get_user_courses(self):
        courses=home_models.Course.objects.filter(Instructor=self,status="approved").count()
        return courses
class LoggedInUser(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE, related_name='logged_in_user')
    session_key = models.CharField(max_length=100, null=True, blank=True)
    
    # def __str__(self):
    #     return self.session_key

@receiver(post_save, sender=User)
def create_user_session(sender, instance, created, **kwargs):
    if created:
        LoggedInUser.objects.create(user=instance)



auth_user=settings.AUTH_USER_MODEL
  

USER_STATUS=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined")
)
class TeacherForms(models.Model):
    teacher=models.ForeignKey(auth_user,on_delete=models.CASCADE)
    status=models.CharField(choices=USER_STATUS,default="pending",max_length=50)
    # code=models.CharField(max_length=50)
    data=models.TextField()    
    def __str__(self):      
        return self.teacher.username

    def get_user_data(self):
        data=json.loads(self.data)
        title=data["title"]
        social=[]
        about_me=data["about_me"]
        for i in data["social"]: 
            if i["facebook"]:
                facebook=i["facebook"]
            else:
                facebook=None
            if i["twitter"]:
                twitter=i["twitter"]
            else:
                twitter=None
            if i["linkedin"]:
                linkedin=i["linkedin"]
            else:
                linkedin=None
        context={"about_me":about_me,"title":title,"facebook":facebook,"linkedin":linkedin,"twitter":twitter}
        return context

