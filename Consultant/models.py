from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q

User=get_user_model()
# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Teacher_Time(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    date=models.DateTimeField(auto_now_add=False)
    from_time=models.TimeField(auto_now_add=False)
    to_time=models.TimeField(auto_now_add=False)
    price=models.FloatField(default=0)
    def __str__(self):
        return self.user.username

        
PAYMENTS=(
    ("Bank Transaction","Bank Transaction"),
    ("Western Union","Western Union"),
    ("Vodafone Cash","Vodafone Cash"),
    ("Paypal","Paypal")
)

class Consultant(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    teacher=models.ForeignKey(Teacher_Time,on_delete=models.CASCADE)
    completed=models.BooleanField(default=False)
    pending=models.BooleanField(default=False)
    zoom=models.TextField(blank=True)
    def __str__(self):
        return self.user.username

# def check_if_user__has_const(user):
#     conslt=Consultant.objects.filter(Q(user=user,completed=False) | Q(user=user,pending=True))
#     return conslt
def upload_consultant_payment(instance,filename):
    return (f"payment/consultant/{instance.user.username}/{filename}")

class Cosultant_Payment(models.Model):
    consult=models.ForeignKey(Consultant,on_delete=models.SET_NULL,null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    method=models.CharField(choices=PAYMENTS,max_length=50)
    payment_image=models.ImageField(upload_to=upload_consultant_payment,null=True)
    transaction_number=models.CharField(max_length=50,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    pending=models.BooleanField(default=False)
    ordered=models.BooleanField(default=False)
    def __str__(self):
        return self.method