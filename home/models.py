from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
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
import json
User=settings.AUTH_USER_MODEL
Quiz= Quiz.models.Quiz()
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
    video=models.FileField(upload_to=upload_course_videos)
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

    def video_duration(self):
        media_info = MediaInfo.parse(self.video)
        duration_in_ms = media_info.tracks[0].duration    
        time_in_sec=duration_in_ms/1000
        print(time_in_sec)
        self.duration =time_in_sec
        self.duration=time.strftime('%H:%M:%S',  time.gmtime(self.duration))
        return self.duration

@receiver(pre_save, sender=Videos)
def pre_save_receiver_video(sender, instance, *args, **kwargs):
    if not instance.slug:
        if Videos.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.my_course.name}-{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug) 
        else:       
            slug=f"{instance.name}"
            instance.slug = slugify(slug) 
    media_info = MediaInfo.parse(instance.video)
    # duration in milliseconds
    duration_in_ms = media_info.tracks[0].duration
    time_in_sec=duration_in_ms/1000
    my_time=time.strftime('%H:%M:%S',  time.gmtime(time_in_sec))
    instance.duration=time_in_sec
    instance.my_course.total_duration()
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
     
class Course(models.Model):
    name=models.CharField(max_length=150)
    videos=models.ManyToManyField(Videos)
    Instructor=models.ForeignKey(User,related_name="instractor",on_delete=models.CASCADE)
    image=models.ImageField(upload_to=upload_course_image)
    students=models.ManyToManyField(User,blank=True)
    duration=models.FloatField(default=0)
    branch=models.ForeignKey(Branch,null=True,on_delete=models.SET_NULL)
    price=models.FloatField(default=0)
    quiz=models.ForeignKey(Quiz,blank=True,null=True,on_delete=models.SET_NULL)
    course_status=models.CharField(choices=CHOICES,max_length=50)
    details=models.TextField()   
    approved=models.BooleanField(default=False)
    stars=models.FloatField(default=0)
    likes=models.PositiveIntegerField(default=0)
    reviews=models.ManyToManyField(Reviews,blank=True,related_name="course_reviews")
    slug=models.SlugField(unique=True,blank=True)
    def __str__(self):  
        return self.name

    def same(self):
        courses=Course.objects.filter(branch=self.branch,approved=True).exclude(id=self.id).order_by("-id")[:4]
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

    def related_events(self):
        events=Events.objects.filter(user=self.Instructor,category=self.branch)[:4]
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
        if self.quiz:
            quiz=self.quiz.questions.first().slug
        else:    
            quiz=None
        return quiz
def random_string_generator(size = 5, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
 
@receiver(pre_save, sender=Course)
def pre_save_receiver(sender, instance, *args, **kwargs):
    instance.duration=0
    if instance.id:
        for i in instance.videos.all():
            instance.videos.add(i)
            media_info = MediaInfo.parse(i.video)
            duration_in_ms = media_info.tracks[0].duration    
            time_in_sec=duration_in_ms/1000
            print(time_in_sec)
            instance.duration +=time_in_sec        
    if not instance.slug: 
        instance.slug = slugify(instance.name)
        if Course.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.name}-{random_string_generator()}"
            instance.slug = slugify(slug)
        else:
            slug=f"{instance.name}"
            instance.slug = slugify(slug)
      

    # def reviews_count(self):
    #     for i in self.reviews.all():
    #         reviews=i

def upload_events_images(instance,filename):
    place=f"events/{instance.user.username}/{instance.name}/{filename}"
    return place

class Events(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    students=models.ManyToManyField(User,related_name="event_students",blank=True)
    category=models.ForeignKey(Branch,on_delete=models.SET_NULL,null=True)
    details=models.TextField()
    image=models.ImageField(upload_to=upload_events_images)
    date=models.DateField()
    start_time=models.TimeField(auto_now_add=False)
    end_time=models.TimeField(auto_now_add=False)
    place=models.CharField(max_length=100)
    expired=models.BooleanField(default=False)
    approved=models.BooleanField(default=False)
    # map=models.CharField(max_length=100)
    slug=models.SlugField(unique=True,blank=True)
    def __str__(self):
        return self.name

    def get_details(self):
        data=json.loads(self.details)
        try:
            zoom=data["zoom"]
        except:
            zoom=None
        details=data["details"]
        context={"zoom":zoom,"details":details}
        return context
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
    ("Bank Transaction","Bank Transaction"),
    ("Western Union","Western Union"),
    ("Vodafone Cash","Vodafone Cash"),
    ("Paypal","Paypal")
)
class Payment(models.Model):
    method=models.CharField(choices=PAYMENTS,max_length=50)
    payment_image=models.ImageField(upload_to=upload_payment_images,null=True)
    transaction_number=models.CharField(max_length=50,null=True)
    course=models.ForeignKey(Course,on_delete=models.SET_NULL,null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    pending=models.BooleanField(default=False)
    ordered=models.BooleanField(default=False)
    def __str__(self):
        return self.method

class News(models.Model):
    name=models.CharField(max_length=200)
    link=models.URLField(blank=True,null=True,default="#",max_length=200)

    def __str__(self):
        return str(self.id)