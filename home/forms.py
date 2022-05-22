from django import forms
from django.forms.widgets import Widget
from .models import *
import os
IMAGE_EXTENSIONS=[".webp",".gif",".png",".jpg",".jpeg"]

class ReviewForm(forms.ModelForm):
    rate=forms.IntegerField()
    class Meta:
        model=Reviews
        fields=["review","rate"]

    def clean_rate(self):
        rate= self.cleaned_data.get("rate")
        if not 5 >= rate >= 1:
            raise forms.ValidationError("invalid rate")
        return rate

PAYMENTS=(
    ("Bank Transaction","Bank Transaction"),
    ("Western Union","Western Union"),
    ("Vodafone Cash","Vodafone Cash"),
  
)
class PaymentMethodForm(forms.Form):
    image=forms.ImageField(required=True,label="Transaction Screenshot")
    number=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Your Transaction Number ID"}),label="Transaction Number")

    def clean(self):
        # try:
        image=self.cleaned_data.get("image")
        if image:
            size=image.size / (1024 * 1024)
            type=os.path.splitext(image.name)[1].lower()
            if size > 2:
                raise forms.ValidationError("image size is more 2 MB")
            elif type not in IMAGE_EXTENSIONS:   
                raise forms.ValidationError(f"image Extension is not valid")
            else:
                image_name=f"payment{os.path.splitext(image.name)[1]}"
                image.name=image_name
        else:
            raise forms.ValidationError("invalid image")
class CashForm(forms.Form):
    payment_image=forms.ImageField(label="IMAGE RECEIPT")    
    number=forms.CharField(max_length=100)
    def clean_payment_image(self):
        try:
            image=self.cleaned_data.get("payment_image")
            size=image.size / (1024 * 1024)
            type=os.path.splitext(image.name)[1]
            if size > 2:
                raise forms.ValidationError("image size is more 2 MB")
            elif type not in IMAGE_EXTENSIONS:   
                raise forms.ValidationError(f"image Extension is not valid")
            else:
                image_name=f"cash{type}"
                image.name=image_name
        except:
            raise forms.ValidationError(f"invalid image")

class SubscribeForm(forms.ModelForm):
    class Meta:
        model=Subscribe
        exclude=["user"]


    def clean_email(self):
        email=self.cleaned_data.get("email")
        if Subscribe.objects.filter(email=email).exists():
            raise forms.ValidationError("this email is already registered in our news")
        return email

class Support_Form(forms.ModelForm):
    class Meta:
        model = Support_Email
        exclude =["user","status"]