from django.db import models
from django.contrib.auth import get_user_model
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
)
class Rejects(models.Model):
    type=models.CharField(choices=TYPE,max_length=50)
    content_id=models.PositiveIntegerField(default=0)
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

  
class Test(models.Model):
    video=models.FileField()