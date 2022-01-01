from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.core.mail import send_mail,send_mass_mail

import string, random
from django.utils import translation
import Quiz.models   
from converter import Converter
from pymediainfo import MediaInfo
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from embed_video.fields import EmbedVideoField
from PIL import Image
import os  
import time
import datetime
import json
from Dashboard.models import Rejects
User=settings.AUTH_USER_MODEL
Quiz= Quiz.models.Quiz()
from django.template.loader import render_to_string
# Create your models here.

def upload_course_image(instance,filename):
    place=f"courses/images/{instance.Instructor}/{filename}"
    return place
def upload_course_videos(instance,filename):
    place=f"courses/videos/{instance.user.username}/{instance.name}/{filename}"
    return place
class Category(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField(unique=True,blank=True,null=True)
    def __str__(self):
        return self.name  
@receiver(pre_save, sender=Category) 
def pre_save_receiver(sender, instance, *args, **kwargs):       
    if instance.slug == None: 
        instance.slug = slugify(instance.name)
        if Category.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug)
        else:
            slug=f"{instance.name}"
            instance.slug = slugify(slug)

class Branch(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    slug=models.SlugField(unique=True,blank=True)
    def __str__(self):
        return self.name


@receiver(pre_save, sender=Branch)
def pre_save_receiver_video(sender, instance, *args, **kwargs):
    if Branch.objects.filter(slug=instance.slug).exists():
        slug=f"{instance.name}-{random_string_generator()}"
        instance.slug = slugify(slug) 
    else:      
        slug=f"{instance.name}"
        instance.slug = slugify(slug) 


CHOICES=(   
    ("on process","on process"),
    ("complete","complete"),
   
)

class Videos(models.Model):
    name=models.CharField(max_length=100)     
    # video=models.FileField(upload_to=upload_course_videos)
    video=models.FileField()
    video_uid=models.CharField(default="0",max_length=200)
    # video=EmbedVideoField()
    # thumbnail=models.ImageField(blank=True,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE) 
    details=models.TextField()
    duration=models.FloatField(default=0)
    my_course=models.ForeignKey("Course",related_name="course",blank=True,null=True,on_delete=models.CASCADE)
    slug=models.SlugField(blank=True,unique=True)
    def __str__(self):
        return self.name

    def get_duration_model(self):
        return time.strftime('%H:%M:%S',  time.gmtime(self.duration))

    # def video_duration(self):
    #     media_info = MediaInfo.parse(self.video)
    #     duration_in_ms = media_info.tracks[0].duration    
    #     time_in_sec=duration_in_ms/1000
    #     print(time_in_sec)
    #     self.duration =time_in_sec
    #     self.duration=time.strftime('%H:%M:%S',  time.gmtime(self.duration))
        # return self.duration
    def total_duration(self):
        self.my_course.duration=0
        self.my_course.save()
        for i in self.my_course.videos.all():
            self.my_course.duration +=i.duration
        self.my_course.save()
        return self.my_course.duration
@receiver(pre_save, sender=Videos)
def pre_save_receiver_video(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)
        if Videos.objects.filter(slug=instance.slug).exists():
            print("hererere")
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug) 
        else:       
            slug=f"{instance.name}"
            instance.slug = slugify(slug) 
    # media_info = MediaInfo.parse(instance.video)
    # # duration in milliseconds
    # duration_in_ms = media_info.tracks[0].duration
    # time_in_sec=duration_in_ms/1000
    # my_time=time.strftime('%H:%M:%S',  time.gmtime(time_in_sec))
    # instance.duration=time_in_sec
    # if instance.video not in instance.my_course.videos.all():
    #     media_info = MediaInfo.parse(instance.video)
    #     duration_in_ms = media_info.tracks[0].duration    
    #     time_in_sec=duration_in_ms/1000
    #     instance.my_course.duration +=time_in_sec

class Teacher_review(models.Model):       
    user=models.ForeignKey(User,related_name="student_review",on_delete=models.CASCADE)
    review=models.TextField(blank=True,null=True)
    rate=models.PositiveIntegerField(default=0)
    teacher=models.ForeignKey(User,related_name="teacher_review",on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username    

    def total_rate(self):
        reviews=Teacher_review.objects.filter(teacher=self.teacher)
        rate=0
        if len(reviews) > 0:
            for i in reviews:
                rate +=i.rate
            total=rate / len(reviews)
        else:   
            total=1
        return total
class Reviews(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    review=models.TextField(blank=True,null=True)
    rate=models.PositiveIntegerField(default=0)
    course=models.ForeignKey("Course",related_name="reviews_course",on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username    
class CheckRejectCourse(models.Manager):
    def get_query_set(self):
        rejects=Rejects.objects.filter(type="course")
        list=[]
        for i in rejects:
            # i.content_id
            list.append(i.content_id)
        course=Course.objects.filter(status="approved").exclude(id__in=list)
        return course
COURSE_STATUS=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined")
)
class Course(models.Model):
    name=models.CharField(max_length=150)
    videos=models.ManyToManyField(Videos)
    Instructor=models.ForeignKey(User,related_name="instractor",on_delete=models.CASCADE)
    image=models.ImageField()
    students=models.ManyToManyField(User,blank=True)
    duration=models.FloatField(default=0)
    branch=models.ForeignKey(Branch,null=True,on_delete=models.SET_NULL)
    price=models.FloatField(default=0)
    discount=models.PositiveIntegerField(default=0)
    quiz=models.ForeignKey(Quiz,blank=True,null=True,on_delete=models.SET_NULL)
    course_status=models.CharField(choices=CHOICES,max_length=50)
    details=models.TextField()   
    status=models.CharField(choices=COURSE_STATUS,max_length=50,default="pending")
    stars=models.FloatField(default=0)
    likes=models.PositiveIntegerField(default=0)
    collection=models.CharField(max_length=200,default="#")     #this is for bunny collection
    reviews=models.ManyToManyField(Reviews,blank=True,related_name="course_reviews")
    slug=models.SlugField(unique=True,blank=True)
    def __str__(self):  
        return self.name

    def same(self):
        courses=Course.objects.filter(branch=self.branch,status="approved").exclude(id=self.id).order_by("-id")[:4]
        return courses
    def get_duration_model(self):
        return time.strftime('%H:%M:%S',  time.gmtime(self.duration))
    def total_duration(self):
        self.duration=0
        for i in self.videos.all():
            media_info = MediaInfo.parse(i.video)
            duration_in_ms = media_info.tracks[0].duration    
            time_in_sec=duration_in_ms/1000
            print(time_in_sec)
            self.duration +=time_in_sec
        my_time=time.strftime('%H:%M:%S',  time.gmtime(self.duration))
        return my_time

    def get_price(self):
        if self.discount > 0:
            price=self.discount
        else:
            price=self.price
        return price
    def related_events(self):
        events=Events.objects.filter(user=self.Instructor,category=self.branch,status="approved")[:4]
        return events

    def total_rate(self):
        if self.reviews.count() > 0:
            rate=0
            for i in self.reviews.all():
                rate +=i.rate
            total=rate / (self.reviews.count())
            print(total)
        else:   
            total=1
        return total
    def calculate_quiz(self):
        if self.quiz:
            questions=self.quiz.questions.count()
        else:
            questions=0
        return questions
    def get_total_quiz(self):
        try:
            if self.quiz:
                quiz=self.quiz.questions.first().slug
            else:    
                quiz=None
        except:
            quiz=None

        return quiz
@receiver(pre_save, sender=Course)
def pre_save_receiver(sender, instance, *args, **kwargs):       
    if not instance.slug: 
        instance.slug = slugify(instance.name)
        if Course.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug)
        else:
            slug=f"{instance.name}"
            instance.slug = slugify(slug)
def random_string_generator(size = 5, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

      

    # def reviews_count(self):
    #     for i in self.reviews.all():
    #         reviews=i

def upload_events_images(instance,filename):
    place=f"events/{instance.user.username}/{instance.name}/{filename}"
    return place

class CheckRejectEvent(models.Manager):
    def get_query_set(self):
        rejects=Rejects.objects.filter(type="events")
        list=[]
        for i in rejects:
            # i.content_id
            list.append(i.content_id)
        events=Events.objects.filter(approved=False).exclude(id__in=list)
        return events

EVENT_STATUS=(
    ("approved","approved"),
    ("declined","declined"),
    ("pending","pending"),
    ("start","start"),
    ("completed","completed")
)
class Events(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    students=models.ManyToManyField(User,related_name="event_students",blank=True)
    category=models.ForeignKey(Branch,on_delete=models.SET_NULL,null=True)
    details=models.TextField()
    image=models.ImageField(upload_to=upload_events_images)
    date=models.DateField()
    status=models.CharField(choices=EVENT_STATUS,max_length=20,default="pending")
    start_time=models.TimeField(auto_now_add=False)
    end_time=models.TimeField(auto_now_add=False)
    place=models.CharField(max_length=100)
    # map=models.CharField(max_length=100)
    slug=models.SlugField(unique=True,blank=True)
    def __str__(self):
        return self.name
    def get_students_events(self):
        course=Course.objects.filter(branch=self.category,status="approved",Instructor=self.user)
        list=[]
        for i in course:
            for b in i.students.all():
                self.students.add(b)
                self.save()
                list.append(b.email)
        message1 =  (f'Event {self.name} start ',
                     f'Event {self.name} has been started , Click The Link to join {self.get_details()["zoom"]}',
        settings.EMAIL_HOST_USER,
       list
       )
        try: 
            send_mass_mail((message1,), fail_silently=False)
        except:
            pass
        return list
    def get_details(self):
        data=json.loads(self.details)
        try:
            zoom=data["zoom"]
        except:
            zoom=None
        details=data["details"]
        context={"zoom":zoom,"details":details}
        return context
    def get_similar_event(self):
        rejects=Rejects.objects.filter(user=self.user,type="events",content_id=self.id).delete()
        return rejects
@receiver(pre_save, sender=Events)
def pre_save_receiver(sender, instance, *args, **kwargs):       
    if not instance.slug: 
        instance.slug = slugify(instance.name)
        if Events.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug)
        else:
            slug=f"{instance.name}"
            instance.slug = slugify(slug)

# class Contact(models.Model):
#     name=

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    course=models.ManyToManyField(Course,blank=True)

    def __str__(self):
        return self.user.username
     
def upload_payment_images(instance,filename):
    place=f"payments/{instance.user.username}/{filename}"
    return place  

PAYMENTS=(
    ("Paymob","Paymob"),
    ("Western Union","Western Union"),
    ("Paypal","Paypal")
)

class CheckRejectPayment(models.Manager):
    def get_query_set(self):
        rejects=Rejects.objects.filter(type="payment")
        list=[]
        for i in rejects:
            # i.content_id
            list.append(i.content_id)
        payment=Payment.objects.filter(status="pending").exclude(id__in=list)
        return payment

PAYMENT_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"),

)
class Payment(models.Model):
    method=models.CharField(choices=PAYMENTS,max_length=50)
    payment_image=models.ImageField(upload_to=upload_payment_images,null=True)
    transaction_number=models.CharField(max_length=50,null=True)
    course=models.ForeignKey(Course,on_delete=models.SET_NULL,null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    def __str__(self):
        return self.method

    def check_if_rejected(self):
        rejects=Rejects.objects.filter(type="payment",content_id=self.id,user=self.user).delete()
        return rejects

class News(models.Model):
    name=models.CharField(max_length=200)
    link=models.CharField(blank=True,null=True,default="#",max_length=200)
    # approved=models.BooleanField(default=False)
    def __str__(self):
        return str(self.id)