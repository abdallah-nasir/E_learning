from django import forms
from django.contrib.auth import get_user_model
from Blogs.models import Blog,Blog_Payment,Prices
from home.models import Course,Branch,Videos,Events,Payment,News
from .models import Rejects
from Consultant.models import Cosultant_Payment,Teacher_Time
from Quiz.models import Question ,Answers
import os
from crum import get_current_request   
User=get_user_model()

class AddBlog(forms.ModelForm):
    image=forms.ImageField(required=True)
    class Meta:
        model=Blog
        fields=["name","details","category","paid","tags","image"]
    def clean_video(self):
        request=get_current_request()
        video=self.cleaned_data.get("video")      
        blog_type=request.GET.get("blog_type")
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
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        image_extentions=[".png",".jpg",",jpeg"]
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in image_extentions:
                raise forms.ValidationError("invalid image extension")
        return image


class BlogTypeForm(forms.ModelForm):
    class Meta:
        model=Blog
        fields=["blog_type"]
class BlogQuoteForm(forms.ModelForm):
    quote=forms.CharField(required=True,max_length=100)
    image=forms.ImageField(required=True)
    class Meta:
        model=Blog
        fields=["name","quote","details","category","paid","tags","image"]
    def clean_image(self):
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        image_extentions=[".png",".jpg",",jpeg"]
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in image_extentions:
                raise forms.ValidationError("invalid image extension")
        return image
class BlogLinkForm(forms.ModelForm):
    link=forms.CharField(required=True,max_length=100)
    image=forms.ImageField(required=True)
    class Meta:
        model=Blog
        fields=["name","link","details","category","paid","tags","image"]

    def clean_image(self):
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        image_extentions=[".png",".jpg",",jpeg"]
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in image_extentions:
                raise forms.ValidationError("invalid image extension")
        return image
class BlogVideoForm(forms.ModelForm):
    video=forms.FileField(label="Video / Audio")
    image=forms.ImageField(required=True)
    class Meta:
        model=Blog
        fields=["name","details","category","paid","tags","video","image"]

    def clean_image(self):
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        image_extentions=[".png",".jpg",",jpeg"]
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in image_extentions:
                raise forms.ValidationError("invalid image extension")
            
        return image
    
    def clean_video(self):
        video=self.cleaned_data.get("video")      
        request=get_current_request()
        blog_type=request.GET.get("blog_type")
        video_extentions=[".3gp",".aa",".aac",".aiff",".webm",".wav",".m4a",".amr",".mp4",".mp3",".avchd",".mkv",".webm",".wmv",".mov"]
        if blog_type == "video" or blog_type == "audio":
            if video is False:
                raise forms.ValidationError("please insert a video / audio")
            else:
                video_type=os.path.splitext(video.name)[1]
                if video_type not in  video_extentions:
                    raise forms.ValidationError("invalid video / audio extension")

        return video
class BlogGalleryForm(forms.ModelForm):
    image=forms.FileField(required=True,widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model=Blog
        fields=["name","details","category","paid","tags","image"]

    def clean_image(self):
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        image_extentions=[".png",".jpg",",jpeg"]
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in image_extentions:
                raise forms.ValidationError("invalid image extension")
        return image

class AddCourse(forms.ModelForm):
    branch=forms.ModelChoiceField(label="Category",queryset=Branch.objects.all())
    # course_image=forms.ImageField(label="image",required=True)
    # videos=forms.FileField()
    class Meta:
        model=Course
        fields=['name',"image","branch","details","price","discount","course_status"]

    def clean_image(self):
        image=self.cleaned_data.get("image")
        request=get_current_request()
        try:
            if request.FILES["image"]:
                image_extentions=[".png",".jpg",",jpeg"]
                image_extension=os.path.splitext(image.name)[1]
                if image_extension.lower() not in image_extentions:
                    raise forms.ValidationError("invalid image extension")
        except:
            pass
        return image

class EditCourse(forms.ModelForm):
    branch=forms.ModelChoiceField(label="Category",queryset=Branch.objects.all())
    image=forms.ImageField(label="image",required=False)
    # videos=forms.FileField()
    class Meta:
        model=Course
        fields=['name',"image","branch","details","price","discount","course_status"]

    def clean_image(self):
        image=self.cleaned_data.get("image")
        request=get_current_request()
        try:
            if request.FILES["image"]:
                image_extentions=[".png",".jpg",",jpeg"]
                image_extension=os.path.splitext(image.name)[1]
                if image_extension.lower() not in image_extentions:
                    raise forms.ValidationError("invalid image extension")
        except:
            pass
        return image

class AddVideo(forms.ModelForm):
    class Meta:
        model=Videos
        fields=['name',"details"]

    def clean_video(self):
        video=self.cleaned_data.get("video")      
        video_extentions=[".3gp",".aa",".aac",".aiff",".webm",".wav",".m4a",".amr",".mp4",".mp3",".avchd",".mkv",".webm",".wmv",".mov",".avi"]
        if video is False:
            raise forms.ValidationError("insert video")

        video_type=os.path.splitext(video.name)[1]
        if video_type.lower() not in  video_extentions:
            raise forms.ValidationError("invalid video extension")
        return video

class EditVideo(forms.ModelForm):
    class Meta:
        model=Videos
        fields=['name',"details"]
    # def clean_video(self):
    #     video=self.cleaned_data.get("video")      
    #     video_extentions=[".3gp",".aa",".aac",".aiff",".webm",".wav",".m4a",".amr",".mp4",".mp3",".avchd",".mkv",".webm",".wmv",".mov"]
    #     if video is False:
    #         raise forms.ValidationError("insert video")

    #     video_type=os.path.splitext(video.name)[1]
    #     if video_type not in  video_extentions:
    #         raise forms.ValidationError("invalid video extension")
    #     return video

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
        if image_extension.lower() not in image_extentions:
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
class NewsForm(forms.ModelForm):
    class Meta:
        model=News
        fields="__all__"
    

class CosultantAddForm(forms.ModelForm):
    date=forms.DateField(widget=DatePickerInput(format='%m/%d/%y'))
    from_time=forms.TimeField(widget=TimePickerInput(format='%H:%M:%S'))
    to_time=forms.TimeField(widget=TimePickerInput(format='%I:%M:%S'))
    class Meta:
        model=Teacher_Time 
        fields="__all__"
        exclude=["user"]

class UploadVideoForm(forms.Form):
    # title=forms.CharField(max_length=50)
    video=forms.FileField()
############################
# Get model details for superuser

class RejectForm(forms.ModelForm):
    subject=forms.CharField()
    message=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Rejects
        fields=["subject","message"]

    # def __init__(self, *args, **kwargs):
    #     super(UserDetail, self).__init__(*args, **kwargs)
    #     for i in self.fields:
    #         self.fields[i].widget.attrs['readonly'] = True
    #     self.fields["message"].widget.attrs['readonly'] = False

DURATION_PRICE=(
    ("monthly","monthly"),
    ("annually","annually")
)
class PriceForm(forms.ModelForm):
    duration=forms.ChoiceField(choices=DURATION_PRICE,required=True)
    class Meta:
        model=Prices
        fields=["name","price","duration","data"]
