from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
import string,random,json,time,mutagen
from cdn.conf import AWS_LOCATION
from django.contrib.auth import get_user_model
User=get_user_model()
# Create your models here.
 
def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")       
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str
def random_string_generator(size = 5, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Category(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Category.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Category, self).save()
    def __str__(self):
        return self.name     
ACTION_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"),
    ("refund","refund"),
    )
STATUS=(
   (1,"videos"),
   (2,"music"),
   (3,"audio book"),
   (4,"e-book")
) 
LIBRARY_TYPE=(
    (1,"audio_book"),
    (2,"music"), 
    (3,"movies"),
    (4,"e_book")
)  
class Comments(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    library=models.IntegerField(choices=LIBRARY_TYPE,default=1)
    content_id=models.IntegerField(null=True)
    comment=models.TextField() 
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username
     
class Audio_Book_Tracks(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    image=models.ImageField()
    book=models.ManyToManyField("Audio_Book",blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    price=models.FloatField(null=True,default=0)
    buyers=models.ManyToManyField(User,related_name="audio_book_user",blank=True)
    comments=models.ManyToManyField(Comments,blank=True)
    data=models.JSONField() 
    status=models.CharField(choices=ACTION_CHOICES,max_length=20,default="pending")
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Audio_Book_Tracks.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Audio_Book_Tracks, self).save()
    def get_data(self):
        data=self.data
        book_data=data["about"] 
        context={"about":book_data}
        return context
    def get_total_duration(self):
        duration=0
        for i in self.book.all():
            duration +=i.duration
        total_time=time.strftime('%H:%M:%S',  time.gmtime(duration))
        return total_time
    def get_price(self):
        try:
            data=self.data
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            if self.price:
                price= self.price
            else: 
                price=0
        return price
    def get_cache_data(self):
        same=Audio_Book_Tracks.objects.filter(status="approved",category=self.category).exclude(id=self.id).select_related("user")[:4]
        context={"same":same}
        return context
    def check_user_in(self,user_id):
        if self.buyers.filter(id=user_id).exists():
            return True
        else:
            return False
    def get_comments(self):
        return Comments.objects.filter(library=1,content_id=self.id).select_related("user")

class Audio_Book(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    data=models.TextField()
    track=models.ForeignKey(Audio_Book_Tracks,related_name="audio_book_track",null=True,on_delete=models.CASCADE)
    duration=models.PositiveIntegerField(null=True)
    is_play=models.BooleanField(default=False)
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Audio_Book.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Audio_Book, self).save()
        

    def get_music(self):
        try:
            data=json.loads(self.data)
            music=data["audio_url"]
        except:
            music=None
        return music

    def check_music(self):
        try:
            data=json.loads(self.data)
            if data["audio_url"]:
                return True
            else:
                return False
        except:
            return False
    def get_duration_model(self):
        total_time=time.strftime('%H:%M:%S',  time.gmtime(self.duration))
        return total_time
class Audio_Tracks(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    image=models.ImageField()
    music=models.ManyToManyField("Music",blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    price=models.FloatField(null=True,default=0)
    buyers=models.ManyToManyField(User,related_name="exist_user",blank=True)
    comments=models.ManyToManyField(Comments,blank=True)
    data=models.TextField() 
    status=models.CharField(choices=ACTION_CHOICES,max_length=20,default="pending")
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    
    def __str__(self):
        return self.name

    def get_price(self):
        try:
            data=json.loads(self.data)
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            if self.price:
                price= self.price
            else:
                price=0
        return price
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Audio_Tracks.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Audio_Tracks, self).save()
    def get_data(self):
        data=json.loads(self.data)
        return data
    def get_total_duration(self):
        duration=0
        for i in self.music.all():
            duration +=i.duration
        total_time=time.strftime('%H:%M:%S',  time.gmtime(duration))
        return total_time
    def get_cache_data(self):
        same=Audio_Tracks.objects.filter(status="approved",category=self.category).exclude(id=self.id).select_related("user")[:4]
        context={"same":same}
        return context
     
    def check_user_in(self,user_id):
        if self.buyers.filter(id=user_id).exists():
            return True
        else:
            return False
    def get_comments(self):
        return Comments.objects.filter(library=2,content_id=self.id).select_related("user")

class Music(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    data=models.TextField()
    track=models.ForeignKey(Audio_Tracks,related_name="music_track",null=True,on_delete=models.CASCADE)
    duration=models.PositiveIntegerField(null=True)
    is_play=models.BooleanField(default=False)
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Music.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Music, self).save()
    def get_duration_model(self):
        return time.strftime('%H:%M:%S',  time.gmtime(self.duration))


    def get_music(self):
        try:
            data=json.loads(self.data)
            music=data["audio_url"]
        except:
            music=None
        return music

    def check_music(self):
        try:
            data=json.loads(self.data)
            if data["audio_url"]:
                return True
            else:
                return False
        except:
            return False
        
class Movies(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=150) 
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    data=models.TextField()
    duration=models.PositiveIntegerField(null=True)
    buyers=models.ManyToManyField(User,blank=True,related_name="movies_user")
    price=models.FloatField(null=True,default=0)
    comments=models.ManyToManyField(Comments,blank=True)
    status=models.CharField(choices=ACTION_CHOICES,max_length=20,default="pending")
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Movies.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Movies, self).save() 
    def get_duration_model(self):
        return time.strftime('%H:%M:%S',  time.gmtime(self.duration))

    def get_related(self):
        movies=Movies.objects.filter(category=self.category).exclude(id=self.id).select_related("category")[:4]
        return movies 
    def get_movie_data(self):
        data=json.loads(self.data)
        summery=data["summery"]
        context={"summery":summery}
        return context
    def get_price(self):
        try:
            data=json.loads(self.data)
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            if self.price:
                price= self.price
            else:
                price=0
        return price
    def check_movies(self):
        try:
            data=json.loads(self.data)
            if data["video"]:
                result=True
            else:
                result=False
        except:
            result=False
        return result
    def get_demo_movie(self):
        data=json.loads(self.data)
        demo_video_url=data["demo_video_url"]
        demo_video_uid=data["demo_video_uid"]
        demo_video_duration=int(data["demo_duration"])
        context={"demo_video_url":demo_video_url,"demo_video_uid":demo_video_uid,"demo_duration":demo_video_duration}
        return context
    def get_movies(self):
        data=json.loads(self.data)
        video_uid=data["video_uid"]
        collection=data["collection_guid"]
        image=data["images"][0]
        video_url=data.get("video")
        context={"collection":collection,"video_uid":video_uid,"video_url":video_url,"image":image}
        return context
    def check_demo_movies(self):
        try:
            data=json.loads(self.data)
            if data["demo_video_url"]:
                result=True
            else:
                result=False
        except:
            result=False
        return result
    def check_duration(self):
        if self.duration:
            if self.duration > 0:
                return True
            else:
                return False
        else:
            return False 
    def get_comments(self):
        return Comments.objects.filter(library=3,content_id=self.id).select_related("user")

def pdf_upload(instance, filename):
    return (f"pdf/{instance.user.username}/{instance.slug}/{instance.pdf}")
     
class E_Book(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    image=models.ImageField()
    pdf = models.FileField(blank=True,null=True,upload_to=pdf_upload)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    data=models.JSONField() 
    buyers=models.ManyToManyField(User,blank=True,related_name="book_users")
    comments = models.ManyToManyField(Comments, blank=True)
    price=models.FloatField(null=True,default=0)
    status=models.CharField(choices=ACTION_CHOICES,max_length=20,default="pending")
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if E_Book.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(E_Book, self).save()

    def __str__(self):
        return self.name 
    def check_pdf(self):
        try:
            pdf=self.pdf.url
            return True
        except:
            return False
    def get_book(self):
        try:
            if self.pdf.url:
                result=f"{AWS_LOCATION}/media/{self.pdf}"
            else:
                result=False
        except:
            result=False
        return result
    def get_price(self):
        try:
            data=self.data
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            price= self.price
        return price
    def get_data_e_book(self):
        data=self.data
        images=data["images"]
        first_image=images[0]
        context={"images":images,"first_image":first_image}
        return context
    
    def get_about(self):
        data=self.data
        try:
            about=data["about"]
        except:
            about=None
        return about
    def get_comments(self):
        return Comments.objects.filter(library=4,content_id=self.id).select_related("user")

    def get_same(self):
        return E_Book.objects.filter(category=self.category,status="approved").exclude(id=self.id).select_related("user")[:4]
class Artist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.CharField(choices=ACTION_CHOICES,default="pending",max_length=10)
    data=models.TextField()
    
    def get_tracks(self):
        tracks=Audio_Tracks.objects.filter(user=self.user,status="approved").select_related("user").order_by("-id")
        return tracks
    def get_music(self):
        music=Music.objects.filter(user=self.user).select_related("user").order_by("-id")
        return music
PAYMENT_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"), 
    ("refund","refund"), 
    )

PAYMENTS=(
    ("bank","bank"),
    ("Western Union","Western Union"),
    ("Paypal","Paypal")
) 
class Library_Payment(models.Model):
    method=models.CharField(choices=PAYMENTS,max_length=100)
    library_type=models.IntegerField(choices=LIBRARY_TYPE,default=3)
    payment_image=models.ImageField(blank=True,null=True)
    transaction_number=models.CharField(max_length=50,null=True)
    amount=models.PositiveIntegerField(default=0)
    content_id=models.IntegerField()
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=10)
    created_at=models.DateField()
    # expired_at=models.DateField(blank=True,null=True)
    expired=models.BooleanField(default=False)

    def __str_(self):return self.method

    def get_movies(self):
        if self.library_type == 3:
            movies=Movies.objects.get(id=self.content_id)
        return movies
    def get_music(self):
        if self.library_type == 2:
            track=Audio_Tracks.objects.get(id=self.content_id)
        return track
    def get_e_book(self):
        if self.library_type == 4:
            track=E_Book.objects.get(id=self.content_id)
        return track
    def check_payment(self):
        if self.expired == True:
            return False
        elif self.status == "declined":
           
            if self.method == "Western Union" or self.method == "bank":
                return True
            else:
                return False
        else:
            return False

    def get_audio_book(self):
        if self.library_type == 1:
            track=Audio_Book_Tracks.objects.get(id=self.content_id)
        return track
    def check_refund(self): 
        if self.expired == True:
            return False
        if self.status != "refund":
            if self.method == "Western Union":
                return False
            else:
                return True
        else:
            return False 