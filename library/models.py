from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
import string,random,json
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


class Audio_Book(models.Model):
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    data=models.TextField()
    students=models.ManyToManyField(User,blank=True)
    duration=models.PositiveIntegerField(null=True)
    price=models.FloatField(null=True)
    status=models.CharField(choices=ACTION_CHOICES,max_length=20,default="pending")
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Audio_Book.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Audio_Book, self).save()
        
    def get_price(self):
        try:
            data=json.loads(self.data)
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            price= self.price
        return price
class Music(models.Model):
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    data=models.TextField()
    students=models.ManyToManyField(User,blank=True)
    duration=models.PositiveIntegerField(null=True)
    price=models.FloatField(null=True)
    status=models.CharField(choices=ACTION_CHOICES,max_length=20,default="pending")

    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Music.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Music, self).save()

    def get_price(self):
        try:
            data=json.loads(self.data)
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            price= self.price
        return price
class Movies(models.Model):
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    data=models.TextField()
    students=models.ManyToManyField(User,blank=True)
    duration=models.PositiveIntegerField(null=True)
    price=models.FloatField(null=True)
    status=models.CharField(choices=ACTION_CHOICES,max_length=20,default="pending")
    slug=models.SlugField(unique=True,blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Movies.objects.filter(slug=self.slug).exists():
                slug=slugify(self.name)
                self.slug =f"{slug}-{random_string_generator()}"
        super(Movies, self).save()

    def get_price(self):
        try:
            data=json.loads(self.data)
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            price= self.price
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
class E_Book(models.Model):
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    data=models.TextField()
    students=models.ManyToManyField(User,blank=True)
    price=models.FloatField(null=True)
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
 
    def get_book(self):
        data=json.loads(self.data)
        try:
            if data["book"]:
                result=True
            else:
                result=False
        except:
            result=False
        return result
    def get_price(self):
        try:
            data=json.loads(self.data)
            if data["discount"]:
                price=data["discount"]
            else:
                price=self.price
        except:
            price= self.price
        return price
    def get_data_e_book(self):
        data=json.loads(self.data)
        images=data["images"]
        first_image=images[0]
        context={"images":images,"first_image":first_image}
        return context
    
PAYMENT_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"),
    ("refund","refund"),
    )

PAYMENTS=(
    ("Paymob","Paymob"),
    ("Western Union","Western Union"),
    ("Paypal","Paypal")
)
class Library_Payment(models.Model):
    method=models.IntegerField(choices=PAYMENTS)
    payment_image=models.ImageField(blank=True,null=True)
    transaction_number=models.CharField(max_length=50,null=True)
    amount=models.PositiveIntegerField(default=0)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    status=models.IntegerField(choices=PAYMENT_CHOICES,default=1)
    created_at=models.DateField()
    expired_at=models.DateField(blank=True,null=True)
    expired=models.BooleanField(default=False)

    def __str_(self):return self.methpd