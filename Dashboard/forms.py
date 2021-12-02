from django import forms
from django.contrib.auth import get_user_model
from Blogs.models import Blog,Blog_Payment
from home.models import Course,Branch,Videos,Events,Payment
from Consultant.models import Cosultant_Payment
from Quiz.models import Question ,Answers
import os
from crum import get_current_request   
User=get_user_model()
class AddBlog(forms.ModelForm):
    image=forms.FileField(required=True,widget=forms.ClearableFileInput(attrs={'multiple': True}))
    link=forms.HiddenInput()
    quote=forms.HiddenInput()
    video=forms.FileField(required=False,label="Video / Audio",widget=forms.FileInput())
    class Meta:
        model=Blog
        # exclude=["user","created_at","updated_at","comments","approved"]
        fields=["blog_type","name","details","video","image","category","paid","tags"]


    def __init__(self,*args,**kwargs):
        super(AddBlog, self).__init__(*args, **kwargs)

        if "blog_type" in self.data:
            type=self.data["blog_type"]
            if type == "link":
                self.fields["link"] = forms.CharField(required=True)
            if type == "quote":
                self.fields["quote"] = forms.CharField(required=True)


    def clean_video(self):
        video=self.cleaned_data.get("video")      
        blog_type=self.cleaned_data.get("blog_type")
        video_extentions=[".3gp",".aa",".aac",".aiff",".webm",".wav",".m4a",".amr",".mp4",".mp3",".avchd",".mkv",".webm",".wmv",".mov"]
        if blog_type == "video":
            if not video:
                raise forms.ValidationError("please insert a video / audio")
            else:
                video_type=os.path.splitext(video.name)[1]
                if video_type not in  video_extentions:
                    raise forms.ValidationError("invalid video / audio extension")

        return video
    def clean_image(self):
        type=self.cleaned_data.get("blog_type")
        request=get_current_request()
        image=request.FILES.getlist("image")
        image_extentions=[".png",".jpg",",jpeg"]
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
            for i in image:
                image_extension=os.path.splitext(i.name)[1]
                print(image_extension)
                if image_extension not in image_extentions:
                    raise forms.ValidationError("invalid image extension")
        return image
    def clean_blog_type(self):
        request=get_current_request()
        type=self.cleaned_data.get("blog_type")
        image=request.FILES.getlist("image")
        link=request.POST.get("link")
        quote=request.POST.get("quote")
        if type == "quote":
            if not quote:
                raise forms.ValidationError("please insert a quote")
        if type == "link":
            if not link:
                raise forms.ValidationError("please insert a link")

        return type


class AddCourse(forms.ModelForm):
    branch=forms.ModelChoiceField(label="Category",queryset=Branch.objects.all())
    # videos=forms.FileField()
    class Meta:
        model=Course
        fields=['name',"image","branch","details","price","discount","course_status"]

    def clean_image(self):
        image=self.cleaned_data.get("image")
        image_extentions=[".png",".jpg",",jpeg"]
        image_extension=os.path.splitext(image.name)[1]
        if image_extension not in image_extentions:
            raise forms.ValidationError("invalid image extension")
        return image

class AddVideo(forms.ModelForm):
    class Meta:
        model=Videos

        fields=['name',"video","details"]

    def clean_video(self):
        video=self.cleaned_data.get("video")      
        video_extentions=[".3gp",".aa",".aac",".aiff",".webm",".wav",".m4a",".amr",".mp4",".mp3",".avchd",".mkv",".webm",".wmv",".mov"]
        video_type=os.path.splitext(video.name)[1]
        if video_type not in  video_extentions:
            raise forms.ValidationError("invalid video extension")
        return video
from bootstrap_datepicker_plus import DatePickerInput,TimePickerInput,DateTimePickerInput
class AddEvent(forms.ModelForm):
    date=forms.DateField(widget=DatePickerInput(format='%m/%d/%y'))
    start_time=forms.TimeField(widget=TimePickerInput(format='%H:%M:%S'))
    end_time=forms.TimeField(widget=TimePickerInput(format='%I:%M:%S'))
    zoom_link=forms.CharField(max_length=300,required=False)
    # about=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Events    
        fields=['name',"category","image","details","date","start_time","end_time","place","zoom_link"]

    def clean_image(self):
        image=self.cleaned_data.get("image")
        image_extentions=[".png",".jpg",",jpeg"]
        image_extension=os.path.splitext(image.name)[1]
        if image_extension not in image_extentions:
            raise forms.ValidationError("invalid image extension")
        return image
class AddQuestion(forms.ModelForm):
    class Meta:
        model=Question
        fields=["title","details"]

class AddAnswer(forms.ModelForm):
    class Meta:
        model=Answers
        fields=["answer","correct"]
############################
# Get model details for superuser
class BlogDetail(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Blog
        fields="__all__"

class Blog_PaymentDetail(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Blog_Payment
        fields="__all__"
class Cosultant_PaymentDetail(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Cosultant_Payment
        fields="__all__"
class CourseDetail(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Course
        fields="__all__"
class EventsDetail(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Events
        fields="__all__"
class PaymentDetail(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Payment
        fields="__all__"
class UserDetail(forms.ModelForm):
    password=forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=User
        fields="__all__"

    def __init__(self, *args, **kwargs):
        super(UserDetail, self).__init__(*args, **kwargs)
        for i in self.fields:
            self.fields[i].widget.attrs['readonly'] = True
        self.fields["message"].widget.attrs['readonly'] = False
