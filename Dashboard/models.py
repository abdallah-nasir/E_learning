from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
# from Home_Models import Course
User=get_user_model()
 
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
    ("blog_payment","blog_payment"),
    ("consultant_payment","consultant_payment"),
)
class Refunds(models.Model):
    type=models.CharField(choices=REFUND_TYPE,max_length=50)
    content_id=models.PositiveIntegerField(default=0)
    transaction_number = models.CharField(max_length=200)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.CharField(max_length=50,choices=status,default="pending")
    def __str__(self):
        return self.type