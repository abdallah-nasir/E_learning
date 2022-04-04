from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
from Dashboard.models import Rejects
User=get_user_model()
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.shortcuts import redirect
import datetime,json
from django.core.cache import cache

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name 

DAYS=(
(6,_("Saturday")),
(7,_("Sunday")),
(1,_("Monday")),
(2,_("Tuesday")),
(3,_("Wednesday")),
(4,_("Thursday")),
(5,_("Friday")),
)
class Teacher_Time(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    date=models.IntegerField(choices=DAYS,default=1)
    start_time=models.TimeField(auto_now_add=False)
    end_time=models.TimeField(auto_now_add=False)
    # from_time=models.TimeField(auto_now_add=False)
    # to_time=models.TimeField(auto_now_add=False)
    price=models.FloatField(default=0)
    available=models.BooleanField(default=True)
    def __str__(self):
        return self.user.username

    def get_teacher_date(self):
        date_number=self.date
        for i,b in DAYS:
            if date_number == i:
                teacher_day = b
        return teacher_day
    def get_teacher_url_consultant(self):
        url=reverse("consultant:get_consultant",kwargs={"slug":self.user.slug})
        path=f"{url}?time={self.id}"
        return path
    
    def day_list_display(self,date):            #to get next 4 weeeks
        now= datetime.date.today()
        iso=now.isoweekday()
        list_days=[]
        if date < iso:
            difference = iso - date
            next= now - datetime.timedelta(days=difference)
            for i in range(1,5):
                all_days=next + datetime.timedelta(weeks=i)
                list_days.append({"day":all_days.strftime("%m/%d/%Y"),"date":all_days.strftime('%A')})
        elif date == iso:
            difference = iso - date
            next= now - datetime.timedelta(days=difference)
            for i in range(1,5):
                all_days=next + datetime.timedelta(weeks=i)
                list_days.append({"day":all_days.strftime("%m/%d/%Y"),"date":all_days.strftime('%A')})
        else:  
            difference = date - iso
            next= now + datetime.timedelta(days=difference)
            for i in range(0,4):
                all_days=next + datetime.timedelta(weeks=i)
                list_days.append({"day":all_days.strftime("%m/%d/%Y"),"date":all_days.strftime('%A')})
        context={"days":list_days}
        return context
    
    def get_available_day(self):
        get_cache=cache.get(f"consultant_data_{self.user}")
        if get_cache:

            data=get_cache 
        else:
            teachers=Teacher_Time.objects.filter(user=self.user,available=True)
            if teachers: 
                sat=teachers.filter(date=6)
                if sat:
                    sat_days=self.day_list_display(date=sat[0].date)
                else:
                    sat_days=None
                sun=teachers.filter(date=7)
                if sun:
                    sun_days=self.day_list_display(date=sun[0].date)
                else:
                        sun_days=None
                mon=teachers.filter(date=1)
                if mon:
                    mon_days=self.day_list_display(date=mon[0].date)
                else:
                    mon_days=None
                tue=teachers.filter(date=2)
                if tue:
                    tue_days=self.day_list_display(date=tue[0].date)
                else:
                    tue_days=None
                wed=teachers.filter(date=3)
                if wed:
                    wed_days=self.day_list_display(date=wed[0].date)
                else:
                    wed_days=None
                thu=teachers.filter(date=4)
                if thu:
                    thu_days=self.day_list_display(date=thu[0].date)
                else:
                    thu_days=None
                fri=teachers.filter(date=5)
                if fri:
                    fri_days=self.day_list_display(date=fri[0].date)
                else:
                    fri_days=None
                data={"sat":sat,"sat_days":sat_days,"sun_days":sun_days,
                        "mon_days":mon_days,"tue_days":tue_days,"wed_days":wed_days,"thu_days":thu_days,"fri_days":fri_days
                        ,"mon":mon,"sun":sun,"tue":tue,"wed":wed,"thu":thu,"fri":fri}
                cache.set(f"consultant_data_{self.user}",data,60*15)
            else:    
                data=None
                return redirect(reverse("consultant:home"))
        return data

    def check_teacher_day(self):            #to check days of teacher
        now= datetime.date.today()
        date=self.date
        iso=now.isoweekday()
        list_days=[]
        if date < iso:
            difference = iso - date
            next= now - datetime.timedelta(days=difference)
            for i in range(1,5):
                all_days=next + datetime.timedelta(weeks=i)
                list_days.append(all_days.strftime("%m/%d/%Y"))
        elif date == iso:
            difference = iso - date
            next= now - datetime.timedelta(days=difference)
            for i in range(1,5):
                all_days=next + datetime.timedelta(weeks=i)
                list_days.append(all_days.strftime("%m/%d/%Y"))
        else:  
            difference = date - iso
            next= now + datetime.timedelta(days=difference)
            for i in range(0,4):
                all_days=next + datetime.timedelta(weeks=i)
                list_days.append(all_days.strftime("%m/%d/%Y"))
        print(list_days)
        return list_days

    def get_next_teacher_day(self):            #to get next day of teacher
        now= datetime.date.today()
        date=self.date
        iso=now.isoweekday()
        if date < iso:
            difference = iso - date
            next= now - datetime.timedelta(days=difference)
            for i in range(1,2):
                all_days=next + datetime.timedelta(weeks=i)
            days=all_days.strftime("%m/%d/%Y")
        elif date == iso:
            difference = date - iso
            next= now + datetime.timedelta(days=difference)
            for i in range(1,2):
                all_days=next + datetime.timedelta(weeks=i)
            days=all_days.strftime("%m/%d/%Y")
        else:   
            difference = date - iso
            next= now + datetime.timedelta(days=difference)
            for i in range(0,1):
                all_days=next + datetime.timedelta(weeks=i)
            days=all_days.strftime("%m/%d/%Y")
        return days
    
    def for_paypal(self):
        url=reverse("consultant:get_consultant",kwargs={"slug":self.user.slug})
        return url
PAYMENTS=(
    ("bank","bank"),
    ("Western Union","Western Union"),
    ("Paypal","Paypal")
)
PAYMENT_CHOICES=(
    ("pending","pending"),
    ("approved","approved"),
    ("declined","declined"),
    ("started","started"),
    ("completed","completed"),
("refund","refund"),
    )



class Consultant(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    teacher=models.ForeignKey(Teacher_Time,on_delete=models.CASCADE)
    start_time=models.TimeField(auto_now_add=True)
    end_time=models.TimeField(auto_now_add=True)
    date=models.DateField(null=True,blank=False,auto_now_add=False)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    zoom=models.TextField(blank=True)
    user_data=models.TextField()
    def __str__(self):
        return self.user.username
    
    def get_user_data(self):
        data=json.loads(self.user_data)
        return data
        

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
("refund","refund"),
)    
class Cosultant_Payment(models.Model):
    teacher=models.ForeignKey(Teacher_Time,on_delete=models.SET_NULL,null=True)
    consultant=models.ForeignKey(Consultant,null=True,blank=True,on_delete=models.SET_NULL)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    method=models.CharField(choices=PAYMENTS,max_length=50)
    payment_image=models.ImageField(upload_to=upload_consultant_payment,null=True)
    transaction_number=models.CharField(max_length=50,null=True)
    amount=models.PositiveIntegerField(default=0)
    created_at=models.DateField(auto_now_add=True)
    status=models.CharField(choices=PAYMENT_CHOICES,default="pending",max_length=50)
    user_data=models.TextField()
    # check_reject=CheckRejectConsultant()
    # objects=models.Manager() 
    def __str__(self):
        return self.method
  
    def get_consultant_date(self):
        cons_date=json.loads(self.user_data)
        date=cons_date["date"]
        return date

    def check_if_rejected(self):
        rejects=Rejects.objects.filter(type="consultant_payment",content_id=self.id,user=self.user).delete()
        return rejects
    def check_payment(self):
        if self.status == "declined":
           
            if self.method == "Western Union" or self.method == "bank":
                return True
            else:
                return False
        else:
            return False

    def check_refund(self): 
        if self.status != "refund":
            if self.method == "Western Union":
                return False
            else:
                return True
        else:
            return False 
class UserDataForm(models.Model):
    teacher=models.ForeignKey(Teacher_Time,on_delete=models.CASCADE)
    data=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateField(auto_now_add=False,null=True)
    accomplished=models.BooleanField(default=False)
    def __str__(self):
        return str(self.id)