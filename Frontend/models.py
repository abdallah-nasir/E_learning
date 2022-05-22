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


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.name
    def get_branch(self):
        return Branch.objects.filter(category__id=self.id).select_related("category")

class Branch(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    def __str__(self):
        return self.name

    def get_faq(self):
        return Faq.objects.filter(branch__id=self.id).select_related("branch")
class Faq(models.Model):
    name = RichTextField()
    branch = models.OneToOneField(Branch,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
