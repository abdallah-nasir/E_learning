from django import forms
from allauth.account.forms import SignupForm,LoginForm
from allauth.socialaccount.forms import SignupForm as SocialSignUpForm
from allauth.socialaccount.models import SocialAccount
import os
from django.db.models.query_utils import Q

from .models import TeacherForms,User
from django.contrib import messages
from django.conf import settings
class MyCustomLoginForm(LoginForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # here you can change the fields
        self.fields['login'] = forms.CharField(label='Username / Email',widget=forms.TextInput(attrs={"placeholder":"Username or Email"}))
    def login(self, *args, **kwargs):
         
        # Add your own processing here.

        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)

ACCOUNT_TYPE=(
    ("student","student"),
    ("teacher","teacher")  
) 
class MyCustomSignupForm(SignupForm):
    account_type=forms.ChoiceField(label="Are You",required=True,choices=ACCOUNT_TYPE)
    phone=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Phone Number"}))
    image=forms.ImageField(label="Profile Picture",required=True)
    
    # about_me=forms.CharField(widget=forms.HiddenInput())
    # title=forms.CharField(widget=forms.HiddenInput())
    def clean(self):
        image=self.cleaned_data.get("image")
        size=image.size / (1024 * 1024)
        type=os.path.splitext(image.name)[1]
        print(size)
        list_type=[".jpg",".jpeg",".png"]
        if size > 2:
            raise forms.ValidationError("image size is more 2 MB")
        elif type not in list_type:   
            raise forms.ValidationError(f"image Extension Must be JPG / JPEG / PNG")
        # if self.cleaned_data.get("account_type") == "teacher":
        #     if self.cleaned_data.get("about_me") == None:
        #         raise forms.ValidationError("You Should Tell us brief about you")
        #     if self.cleaned_data.get("title") == None:
        #         raise forms.ValidationError("Title is missing")      
    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)
        account_type=self.cleaned_data["account_type"]
        user.account_type=account_type
        user.phone=self.cleaned_data["phone"]
        user.image=self.cleaned_data["image"]
        user.first_name=user.username
        # if self.cleaned_data["account_type"] == "teacher":
        #     user.about_me=self.cleaned_data["about_me"]
        #     user.title=self.cleaned_data["about_me"]
        user.save()
        if user.account_type == "teacher":
            user.is_active = False
            user.save()
            messages.success(request,"you have created your Teacher Account and our Team Will be in Touch with you soon to Activate Your account")
        return user
   
class MyCustomSocialSignupForm(SocialSignUpForm):
    account_type=forms.ChoiceField(required=True,choices=ACCOUNT_TYPE)
    phone=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Phone Number"}))
    image=forms.ImageField(required=True)


    def clean(self):
        image=self.cleaned_data.get("image")
        print(image)
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
        account_type=self.cleaned_data["account_type"]
        user.account_type=account_type
        user.phone=self.cleaned_data["phone"]       
        user.image=self.cleaned_data["image"]
        user.save()
        if user.account_type == "teacher":
            user.is_active = False
            user.save()
            messages.success(request,"you have created your Teacher Account and our Team Will be in Touch with you soon to Activate Your account")
        # Add your own processing here.

        # You must return the original result.
        return user

class Teacher_Form(forms.ModelForm):
    username=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Username / Email"}))
    title=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your Job Title"}))
    about_me=forms.CharField(widget=forms.Textarea(attrs={"placeholder":"Tell us more about you"}))

    # password=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Your Password"}))
    facebook=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your facebook link"}))
    linkedin=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your linkedin link"}))
    twitter=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your twitter link"}))
    # google_plus=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Your google plus link"}))
    code=forms.CharField(max_length=100,widget=forms.TextInput(attrs={"placeholder":"Code From Email Sent to You"}))
    class Meta:
        model=TeacherForms
        fields=["username","code","title","about_me","facebook","linkedin","twitter"]


    def clean_username(self): 
        username=self.cleaned_data["username"]
        teacher=User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))
        if teacher.exists():
            if teacher[0].account_type !="teacher" and teacher[0].is_active == True:
                raise forms.ValidationError("not a teacher account")
        else:
            raise forms.ValidationError("invalid user")
        return username

    def clean_code(self): 
        name=self.cleaned_data.get("username")
        code=self.cleaned_data["code"]
        if code == "0":
            raise forms.ValidationError("code cant be 0")
        teacher=User.objects.filter(Q(username__iexact=name) | Q(email__iexact=name))
        if teacher.exists():
            if teacher[0].account_type !="teacher" and teacher[0].is_active == True and teacher[0].code != code:
                raise forms.ValidationError("invalid user")
        else:
            raise forms.ValidationError("invalid code")
        return code   


    def clean_facebook(self): 
        facebook=self.cleaned_data.get("facebook")
        print(facebook[0:25])
        if facebook[0:25] != "https://www.facebook.com/":
            raise forms.ValidationError("invalid url")
        return facebook   
    
    def clean_linkedin(self): 
        linkedin=self.cleaned_data.get("linkedin")
       
        if linkedin[0:25] != "https://www.linkedin.com/":
            raise forms.ValidationError("invalid url")
        return linkedin  
    
    def clean_twitter(self): 
        twitter=self.cleaned_data.get("twitter")
       
        if twitter[0:20] != "https://twitter.com/":
            raise forms.ValidationError("invalid url")
        return twitter   

    # def clean_google_plus(self): 
    #     google_plus=self.cleaned_data.get("google_plus")
       
    #     if google_plus[0:25] != "https://www.facebook.com/":
    #         raise forms.ValidationError("invalid url")
    #     return google_plus   