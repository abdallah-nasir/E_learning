from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
from Dashboard.models import Rejects
User=get_user_model()
# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Teacher_Time(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    date=models.DateField(auto_now_add=False)
    from_time=models.TimeField(auto_now_add=False)
    to_time=models.TimeField(auto_now_add=False)
    price=models.FloatField(default=0)
    available=models.BooleanField(default=True)
    def __str__(self):
        return self.user.username

        
PAYMENTS=(
    ("Paymob","Paymob"),
    ("Western Union","Western Union"),
    ("Paypal","Paypal")
)
PAYMENT_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"),
    ("completed","completed"),

    )
class Consultant(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    teacher=models.ForeignKey(Teacher_Time,on_delete=models.CASCADE)
    # completed=models.BooleanField(default=False)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    zoom=models.TextField(blank=True)
    def __str__(self):
        return self.user.username

# def check_if_user__has_const(user):
#     conslt=Consultant.objects.filter(Q(user=user,completed=False) | Q(user=user,pending=True))
#     return conslt
def upload_consultant_payment(instance,filename):
    return (f"payment/consultant/{instance.user.username}/{filename}")

class CheckRejectConsultant(models.Manager):
    def get_query_set(self):
        rejects=Rejects.objects.filter(type="consultant_payment")
        list=[]
        for i in rejects:
            # i.content_id
            list.append(i.content_id)
        consult=Cosultant_Payment.objects.filter(status="pending").exclude(id__in=list)
        return consult
PAYMENT_CHOICES=(
("pending","pending"),
("approved","approved"),   
("declined","declined"),

)    
class Cosultant_Payment(models.Model):
    consult=models.ForeignKey(Consultant,on_delete=models.SET_NULL,null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    method=models.CharField(choices=PAYMENTS,max_length=50)
    payment_image=models.ImageField(upload_to=upload_consultant_payment,null=True)
    transaction_number=models.CharField(max_length=50,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    # check_reject=CheckRejectConsultant()
    # objects=models.Manager()
    def __str__(self):
        return self.method

    def check_if_rejected(self):
        rejects=Rejects.objects.filter(type="consultant_payment",content_id=self.id,user=self.user).delete()
        return rejects