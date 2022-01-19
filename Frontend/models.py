from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.

class Terms(models.Model):
    text=RichTextField()

    def __str__(self):
        return str(self.id)


class Privacy(models.Model):
    text=RichTextField()

    def __str__(self):
        return str(self.id)