from django import forms
from allauth.account.forms import SignupForm,LoginForm
from allauth.socialaccount.forms import SignupForm as SocialSignUpForm
from allauth.socialaccount.models import SocialAccount
import os
from django.db.models.query_utils import Q
from django.core.mail import send_mail,EmailMessage
from home.models import Payment
from Consultant.models import  Cosultant_Payment
from Blogs.models import Blog_Payment
from .models import TeacherForms,User
from django.contrib import messages
from django.conf import settings
import random,string,requests
from crum import get_current_request   
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from phonenumber_field.formfields import PhoneNumberField

Storage_Api=os.environ["Storage_Api"]
library_id=os.environ["library_id"]
storage_name=os.environ["storage_name"]
agartha_cdn=os.environ["agartha_cdn"]
def random_string_generator(size=7, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
class MyCustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # here you can change the fields
        self.fields['login'] = forms.CharField(label='Username / Email',widget=forms.TextInput(attrs={"placeholder":"Username or Email"}))
    def login(self, *args, **kwargs):
         
        # Add your own processing here.

        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)

GENDER=(
    ("male","male"),
    ("female","female")  
) 
class MyCustomSignupForm(SignupForm):
    gender=forms.ChoiceField(label="Are You",required=True,choices=GENDER)
    phone=PhoneNumberField(required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    terms_privacy=forms.BooleanField(required=True)
    def clean(self):
        image=self.cleaned_data.get("image")
        if image:
            size=image.size / (1024 * 1024)
            type=os.path.splitext(image.name)[1]
            print(size)
            list_type=[".jpg",".jpeg",".png"]
            if size > 2:
                raise forms.ValidationError("image size is more 2 MB")
            elif type not in list_type:   
                raise forms.ValidationError(f"image Extension Must be JPG / JPEG / PNG")
    def clean_phone(self):
        phone=self.cleaned_data.get("phone")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("User with that phone number is already exists")
        return phone
    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)
        gender=self.cleaned_data["gender"]
        user.gender=gender
        user.phone=self.cleaned_data["phone"]
        image=request.POST.get("image")
        if gender == "male":
            user.account_image=f"https://{agartha_cdn}/default_image/male.jpg"
        elif gender == "female":
            user.account_image=f"https://{agartha_cdn}/default_image/female.jpg"
        user.first_name=user.username

        user.save()
        return user
   
class MyCustomSocialSignupForm(SocialSignUpForm):
    gender=forms.ChoiceField(label="Are You",required=True,choices=GENDER)
    phone=PhoneNumberField(required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    terms_privacy=forms.BooleanField(required=True)

    def clean_phone(self):
        phone=self.cleaned_data.get("phone")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("User with that phone number is already exists")
        return phone
    def clean(self):
        image=self.cleaned_data.get("image")
        print(image)
        if image:
            size=image.size / (1024 * 1024)
            type=os.path.splitext(image.name)[1]
            print(size)
            list_type=[".jpg",".jpeg",".png"]
            if size > 2:
                raise forms.ValidationError("image size is more 2 MB")
            elif type not in list_type:   
                raise forms.ValidationError(f"image Extension Must be JPG / JPEG / PNG")

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSocialSignupForm, self).save(request)
        gender=self.cleaned_data["gender"]
        user.gender=gender
        user.phone=self.cleaned_data["phone"]
        image=request.POST.get("image")
        if gender == "male":
            user.account_image=f"https://{agartha_cdn}/default_image/male.jpg"
        elif gender == "female":
            user.account_image=f"https://{agartha_cdn}/default_image/female.jpg"
        user.first_name=user.username
        # if self.cleaned_data["account_type"] == "teacher":
        #     user.about_me=self.cleaned_data["about_me"]
        #     user.title=self.cleaned_data["about_me"]
        user.save()
        # if user.account_type == "teacher":
        #     user.code=random_string_generator()

        #     user.is_active = False
        #     user.save()
        #     msg = EmailMessage(subject="Account Created", body=f"you have created your Teacher Account and our Team Will be in Touch with you soon to Activate Your account, \n use this code to complete your profile info \
        #                        your code:{user.code} \n url:{request.scheme}://{request.META['HTTP_HOST']}/profile/validate/teacher/", from_email=settings.EMAIL_HOST_USER, to=[user.email])
        #     msg.content_subtype = "html"  # Main content is now text/html
        #     msg.send()
        #     messages.success(request,"you have created your Teacher Account and our Team Will be in Touch with you soon to Activate Your account")
        return user




class Teacher_Form(forms.ModelForm):
    title=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your Job Title"}))
    about_me=forms.CharField(widget=forms.Textarea(attrs={"placeholder":"Tell us more about you"}))
    # password=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Your Password"}))
    facebook=forms.CharField(required=False,max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your facebook link"}))
    linkedin=forms.CharField(required=False,max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your linkedin link"}))
    twitter=forms.CharField(required=False,max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your twitter link"}))
    # google_plus=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your google plus link"}))
    class Meta:
        model=TeacherForms
        fields=["title","about_me","facebook","linkedin","twitter"]


    def clean_username(self): 
        username=self.cleaned_data["username"]
        teacher=User.objects.filter(Q(username__iexact=username,account_type="teacher",is_active=False) | Q(email__iexact=username,account_type="teacher",is_active=False))
        if teacher.exists():
            pass
        else:
            raise forms.ValidationError("invalid user")
        return username



    def clean_facebook(self): 
        facebook=self.cleaned_data.get("facebook")
        print(facebook[0:25])
        if facebook and facebook[0:25] != "https://www.facebook.com/":
            raise forms.ValidationError("invalid url")
        return facebook   
    
    def clean_linkedin(self): 
        linkedin=self.cleaned_data.get("linkedin")
       
        if linkedin and linkedin[0:25] != "https://www.linkedin.com/":
            raise forms.ValidationError("invalid url")
        return linkedin  
    
    def clean_twitter(self): 
        twitter=self.cleaned_data.get("twitter")
       
        if twitter and twitter[0:20] != "https://twitter.com/":
            raise forms.ValidationError("invalid url")
        return twitter   

    # def clean_google_plus(self): 
    #     google_plus=self.cleaned_data.get("google_plus")
       
    #     if google_plus[0:25] != "https://www.facebook.com/":
    #         raise forms.ValidationError("invalid url")
    #     return google_plus   
from django.contrib.auth import get_user_model
User=get_user_model()
class ChangeUserDataForm(forms.ModelForm):
    account_image=forms.ImageField(required=False)
    phone=PhoneNumberField(required=True)
    class Meta:
        model=User
        fields=["account_image","first_name","last_name","phone",]

    def clean_phone(self):
        phone=self.cleaned_data.get("phone")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("User with that phone number is already exists")
        return phone
class ChangeTeacherDataForm(forms.ModelForm):
    account_image=forms.ImageField(required=False)
    facebook=forms.CharField(required=False,max_length=120,widget=forms.TextInput(attrs={"placeholder":"Your facebook link"}))
    linkedin=forms.CharField(required=False,max_length=120,widget=forms.TextInput(attrs={"placeholder":"Your linkedin link"}))
    twitter=forms.CharField(required=False,max_length=120,widget=forms.TextInput(attrs={"placeholder":"Your twitter link"}))
    about_me=forms.CharField(widget=forms.Textarea())
    title=forms.CharField(max_length=120)
    phone=PhoneNumberField(required=True)
    class Meta:
        model=User
        fields=["account_image","first_name","last_name","phone","facebook","twitter","linkedin","title","about_me"]
        extra_kwargs={"first_name":{"required":True},"last_name":{"required":True}}
    def clean_facebook(self): 
        facebook=self.cleaned_data.get("facebook")
        print(facebook[0:25])
        if facebook and facebook[0:25] != "https://www.facebook.com/":
            raise forms.ValidationError("invalid url")
        return facebook   
    
    def clean_linkedin(self): 
        linkedin=self.cleaned_data.get("linkedin")
       
        if linkedin and linkedin[0:25] != "https://www.linkedin.com/":
            raise forms.ValidationError("invalid url")
        return linkedin  
    
    def clean_twitter(self): 
        twitter=self.cleaned_data.get("twitter")
       
        if twitter and twitter[0:20] != "https://twitter.com/":
            raise forms.ValidationError("invalid url")
        return twitter  
class BlogPaymentFom(forms.ModelForm):
    payment_image=forms.ImageField(required=False)
    class Meta:
        model=Blog_Payment
        fields=["payment_image","transaction_number"]


class CoursePaymentFom(forms.ModelForm):
    payment_image=forms.ImageField(required=False)
    class Meta:
        model=Payment
        fields=["payment_image","transaction_number"]

class ConsultantPaymentFom(forms.ModelForm):
    payment_image=forms.ImageField(required=False)
    class Meta:
        model=Cosultant_Payment
        fields=["payment_image","transaction_number"]


class CodeForm(forms.Form):
    email=forms.EmailField(required=True,widget=forms.EmailInput(attrs={"placeholder":"Enter your Email"}))
  