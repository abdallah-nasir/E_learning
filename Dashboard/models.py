from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from home import models as Home_Models
import json
from django.apps import apps
# Course = apps.get_model('home', 'Course')

# from Home_Models import Course
User=get_user_model()
def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str
# Create your models here.
TYPE=(
    ("course","course"),  
    ("blogs","blogs"),
    ("blog_payment","blog_payment"),
    ("consultant_payment","consultant_payment"),
    ("events","events"),
    ("payment","payment"),
    ("teacher","teacher"),
    ("add_user","add_user")
)
class Rejects(models.Model):
    type=models.CharField(choices=TYPE,max_length=50)
    content_id=models.PositiveIntegerField(default=0)
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

status=(
    ("pending",("pending")),
    ("approved",("approved")),
    ("declined",("declined")),
)
class AddStudentCourse(models.Model):
    teacher=models.ForeignKey(User,related_name="course_teacher",on_delete=models.CASCADE)
    student=models.ForeignKey(User,related_name="course_student",on_delete=models.CASCADE)
    course=models.ForeignKey(settings.COURSE_MODEL,on_delete=models.CASCADE)
    status=models.CharField(choices=status,max_length=50)

    def  __str__(self):
        return self.teacher.username
  
REFUND_TYPE=(
    ("course_payment","course_payment"),
    ("consultant_payment","consultant_payment"),
    ("blog_payment","blog_payment"),
    ("movie_payment","movie_payment"),
    ("music_payment","music_payment"),
    ("audio_book_payment","audio_book_payment"),
    ("e_book_payment","e_book_payment"),

)
class Refunds(models.Model): 
    type=models.CharField(choices=REFUND_TYPE,max_length=50)
    content_id=models.PositiveIntegerField(default=0)
    transaction_number = models.CharField(max_length=200)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.CharField(max_length=50,choices=status,default="pending")
    data=models.TextField() 
    def __str__(self):
        return self.type

    def get_refund_data(self):
        data=json.loads(self.data)
        method=data["method"]
        amount=data["amount"]
        my_data=data["data"]
        payment_id=data["payment_id"]
        context={"method":method,"amount":amount,"data":my_data,"payment_id":payment_id}
        return context
DOMAINS=(
    (1,"agartha"),
    (2,"kemet")
)
class Ads(models.Model): 
    course=models.ForeignKey(settings.COURSE_MODEL,on_delete=models.CASCADE)
    domain_type=models.IntegerField(choices=DOMAINS,default=1)

    def __str__(self):
        return self.course.name 
    
    def get_domain(self):
        for i in DOMAINS:
            while self.domain_type == i[0]:
                domain=i[1]
                break
        return domain 
    