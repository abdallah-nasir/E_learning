from django import forms
from django.contrib.auth import get_user_model
from Blogs.models import Blog,Blog_Payment,Prices
from Blogs.models import Category as Blog_Category
from Frontend.models import *
from home.models import Course,Branch,Videos,Events,Payment,News,Category,Support_Email
from .models import Rejects,AddStudentCourse,Refunds
from Consultant.models import Cosultant_Payment,Teacher_Time,Consultant
from Consultant.models import Category as Consultant_Category

from Quiz.models import Question ,Answers,Certification
import os
from django.db.models import Q
from crum import get_current_request   
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
import datetime as compare_time
from datetime import date,datetime,time
from taggit.forms import *
from taggit.models import Tag
User=get_user_model()
Audio_Extension=[".3gp",".aa",".aac",".aiff",".wav",".m4a",".amr",".mp3",".webm",".wmv",".mkv"]
Video_Extension=[".webm",".mkv",".flv",".avi",".wmv",".rmvb",".amv",".mp4",".m4p",".mpg",".mpeg",".m4v",".3gp"]
IMAGE_EXTENSIONS=[".webp",".gif",".png",".jpg",".jpeg"]
class AddBlog(forms.ModelForm):
    image=forms.ImageField(required=True)
    class Meta:  
        model=Blog
        fields=["name_en","name_ar","details","category","paid","tags","image"]
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
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in IMAGE_EXTENSIONS:
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
        fields=["name_en","name_ar","quote","details","category","paid","image"]
    def clean_image(self):
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in IMAGE_EXTENSIONS:
                raise forms.ValidationError("invalid image extension")
        return image
class BlogLinkForm(forms.ModelForm):
    link=forms.CharField(required=True,max_length=100)
    image=forms.ImageField(required=True)
    class Meta:
        model=Blog
        fields=["name_en","name_ar","link","details","category","paid","image"]

    def clean_image(self):
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in IMAGE_EXTENSIONS:
                raise forms.ValidationError("invalid image extension")
        return image
    
class BlogVideoForm(forms.ModelForm):
    video=forms.FileField(required=True,label="Video")
    class Meta:
        model=Blog
        fields=["video"]
    
    def clean_video(self):
        video=self.cleaned_data["video"]      
        video_type=os.path.splitext(video.name)[1]
        if video_type not in  Video_Extension:
            raise forms.ValidationError("invalid video extension")
        return video

class BlogAudioForm(forms.ModelForm):
    video=forms.FileField(required=True,label="Audio")
    class Meta:
        model=Blog
        fields=["video"]
     
    def clean_video(self):
        video=self.cleaned_data.get("video")     
        video_type=os.path.splitext(video.name)[1]
        if video_type.lower() not in Audio_Extension:
            raise forms.ValidationError("invalid audio extension")
        return video
class BlogGalleryForm(forms.ModelForm):
    image=forms.FileField(required=True,widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model=Blog
        fields=["name_en","name_ar","details","category","paid","image"]

    def clean_image(self):
        request=get_current_request()
        type=request.GET.get("blog_type")
        image=request.FILES.getlist("image")
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        for i in image:
            image_extension=os.path.splitext(i.name)[1]
            print(image_extension)
            if image_extension.lower() not in IMAGE_EXTENSIONS:
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
                image_extension=os.path.splitext(image.name)[1]
                if image_extension.lower() not in IMAGE_EXTENSIONS:
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
                image_extension=os.path.splitext(image.name)[1]
                if image_extension.lower() not in IMAGE_EXTENSIONS:
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

class AddEvent(forms.ModelForm):
    date=forms.DateField(required=True,widget=DatePicker(options={'minDate': f"{date.today()}"}, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }))
    start_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p"],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
                "format":"H M S"
                
            }))
    end_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p"],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
            }))
    zoom_link=forms.CharField(max_length=300,required=False)
    class Meta:
        model=Events    
        fields=['name',"category","image","details","date","start_time","end_time","place","zoom_link"]
        # fields=["date","start_time","end_time"]
    def clean_image(self):
        image=self.cleaned_data.get("image")
        image_extentions=[".png",".jpg",",jpeg"]
        if image_extension.lower() not in IMAGE_EXTENSIONS:
            raise forms.ValidationError("invalid image extension")
        return image
    def clean_date(self):
        date=self.cleaned_data.get("date")
        if date:
            today=date.today()
            if date < today:
                raise forms.ValidationError("time is already passed")
        return date
    def clean(self):
        request=get_current_request()
        date=self.cleaned_data.get("date")
        start=request.POST.get("start_time")
        end=request.POST.get("end_time")
        start_time=datetime.strptime(f"{start}","%I:%M:%S %p").time()
        end_time=datetime.strptime(f"{end}","%I:%M:%S %p").time()
        category=self.cleaned_data.get("category")
        calculate=datetime.strptime(f"{end}","%I:%M:%S %p")-datetime.strptime(f"{start}","%I:%M:%S %p")
        print(start_time,end_time)
        if start_time < end_time:
            time_betwen = calculate.seconds/60
            if time_betwen < 15:
                raise forms.ValidationError("time must be more than 15 minute")
        else:
            raise forms.ValidationError("invalid end time")
        if start_time and end_time:
            first=start_time.strftime("%H:%M:%S")
            second=end_time.strftime("%H:%M:%S")
            print(first,second)
            if Events.objects.filter(Q(date=date,start_time__range=(first,second)) | Q(date=date,end_time__range=(first,second))).exists():
                print("here")
                raise forms.ValidationError("start time is unavailable now")
class Edit_event(forms.ModelForm):
    date=forms.DateField(required=True,widget=DatePicker(options={'minDate': f"{date.today()}"}, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }))
    start_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p"],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
                "format":"H M S"
                
            }))
    end_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p"],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
            }))
    zoom_link=forms.CharField(max_length=300,required=False)
    image=forms.ImageField(required=False)
    # about=forms.CharField(widget=forms.Textarea())
    class Meta:
        model=Events    
        fields=['name',"category","image","details","date","start_time","end_time","place","zoom_link"]

    def clean_image(self):
        image=self.cleaned_data.get("image")
        if image:
            image_extension=os.path.splitext(image.name)[1]
            if image_extension.lower() not in IMAGE_EXTENSIONS:
                raise forms.ValidationError("invalid image extension")
        return image
    def clean_date(self):
        date=self.cleaned_data.get("date")
        if date:
            today=date.today()
            if date < today:
                raise forms.ValidationError("time is already passed")
        return date
    def clean(self):
        request=get_current_request()
        date=self.cleaned_data.get("date")
        start=request.POST.get("start_time")
        end=request.POST.get("end_time")
        start_time=datetime.strptime(f"{start}","%I:%M:%S %p").time()
        end_time=datetime.strptime(f"{end}","%I:%M:%S %p").time()
        category=self.cleaned_data.get("category")
        calculate=datetime.strptime(f"{end}","%I:%M:%S %p")-datetime.strptime(f"{start}","%I:%M:%S %p")
        print(start_time,end_time)
        if start_time < end_time:
            time_betwen = calculate.seconds/60
            if time_betwen < 15:
                raise forms.ValidationError("time must be more than 15 minute")
        else:
            raise forms.ValidationError("invalid end time")
        if start_time and end_time:
            first=start_time.strftime("%H:%M:%S")
            second=end_time.strftime("%H:%M:%S")
            print(first,second)
            if Events.objects.filter(Q(date=date,start_time__range=(first,second)) | Q(date=date,end_time__range=(first,second))).exists():
                print("here")
                raise forms.ValidationError("start time is unavailable now")

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
        fields=["name","name_ar","link"]
    

class CosultantAddForm(forms.ModelForm): 
    start_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p"],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
                "format":"H M S",
            
                  
                
            }))
    end_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p"],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
                "format":"H M S"
                
            }))
    class Meta:
        model=Teacher_Time 
        fields="__all__"
        exclude=["user"]
    def clean_price(self):
        price=self.cleaned_data.get("price")
        if int(price) <= 0:
            raise forms.ValidationError("invalid price")
        return price

class SessionForm(forms.ModelForm):
    start_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p",],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
                "format":"H M S",
                
            }))   
    end_time=forms.TimeField(required=True,input_formats=["%H:%M:%S %p"],widget=TimePicker(attrs={
                'append': 'fa fa-clock-o',
                'icon_toggle': True,
                "format":"H M S"
                
            }))
    zoom=forms.CharField(required=True,widget=forms.TextInput())

    class Meta:
        model=Consultant 
        fields="__all__"
        exclude=["status","date","user_data","teacher","user"]

class ConsultantCategoryForm(forms.ModelForm):
    class Meta:
        model=Consultant_Category 
        fields="__all__"
        
class UploadVideoForm(forms.Form):
    video=forms.FileField()
    def clean_video(self):
        video=self.cleaned_data.get("video")
        video_extension=os.path.splitext(video.name)[1]
        print(video_extension)
        if video_extension.lower() not in Video_Extension:
            raise forms.ValidationError("invalid video extension")
        return video 
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


class AddUserToCourseForm(forms.Form):
    student=forms.CharField(max_length=30,required=True,widget=forms.TextInput(attrs={"placeholder":"student username"}))
    course=forms.ModelChoiceField(queryset=Course.objects.none())

    def clean_student(self):
        user=self.cleaned_data["student"]
        if User.objects.filter(username=user).exists():
            pass
        else:
            raise forms.ValidationError("invalid username")

    def clean_course(self):
        request=get_current_request()
        course=self.cleaned_data["course"]
        if Course.objects.filter(Instructor=request.user,name=course,status="approved").exists():
            pass
        else:
            raise forms.ValidationError("invalid course")

    def __init__(self, *args, **kwargs):
        super(AddUserToCourseForm, self).__init__(*args, **kwargs)
        request=get_current_request()
        self.fields["course"].queryset = Course.objects.filter(Instructor=request.user,status="approved")


class AddUserDirector(forms.Form):
    user=forms.CharField(max_length=30,required=True,widget=forms.TextInput(attrs={"placeholder":"username or email"}))
    def clean_user(self):
        user=self.cleaned_data["user"]
        if User.objects.filter(Q(username=user,account_type="teacher") | Q(email=user,account_type="teacher")).exists():
            pass
        else:
            raise forms.ValidationError("invalid username")


class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields="__all__"
        extra_kwargs={"image":{"required":True}}
        exclude=["slug"]
    def clean_image(self):
        request=get_current_request()
        image=request.FILES.get("image")
        image_extension=os.path.splitext(image.name)[1]
        if image_extension.lower() not in IMAGE_EXTENSIONS:
            raise forms.ValidationError("invalid image extension")
        return image
class BranchForm(forms.ModelForm):
    class Meta:
        model=Branch
        fields="__all__"
        exclude=["slug"]
class BlogForm(forms.ModelForm):
    class Meta:
        model=Blog_Category
        fields="__all__"
        exclude=["slug"]


class TermsForm(forms.ModelForm):
    class Meta:
        model=Terms
        fields="__all__"
        exclude=["text_en"]

class PrivacyForm(forms.ModelForm):
    class Meta:
        model=Privacy
        fields="__all__"
        exclude=["text_en"]

class Support_Email_Form(forms.ModelForm):
    class Meta:
        model=Support_Email
        fields=["subject","message"]
  

class Update_Certification(forms.ModelForm):
    class Meta:
        model=Certification
        fields=["image"]
        extra_kwargs={"image":{"required":True}}

    def clean_image(self):
        request=get_current_request()
        image=request.FILES.get("image")
        image_extension=os.path.splitext(image.name)[1]
        if image_extension.lower() not in IMAGE_EXTENSIONS:
            raise forms.ValidationError("invalid image extension")
        return image
class Refunds_Form(forms.ModelForm):
    class Meta:
        model=Refunds
        exclude=["user","content_id","status","data"]
        # extra_kwargs={"image":{"required":True}}


class BlogPaymentFom(forms.ModelForm):
    payment_image=forms.ImageField(required=False)
    class Meta:
        model=Blog_Payment
        fields=["payment_image","transaction_number"]

    def clean_payment_image(self):
        request=get_current_request()
        image=request.FILES.get("payment_image")
        image_extension=os.path.splitext(image.name)[1]
        if image_extension.lower() not in IMAGE_EXTENSIONS:
            raise forms.ValidationError("invalid image extension")
        return image
class CoursePaymentFom(forms.ModelForm):
    payment_image=forms.ImageField(required=False)
    class Meta:
        model=Payment
        fields=["payment_image","transaction_number"]
    def clean_payment_image(self):
        request=get_current_request()
        image=request.FILES.get("payment_image")
        image_extension=os.path.splitext(image.name)[1]
        if image_extension.lower() not in IMAGE_EXTENSIONS:
            raise forms.ValidationError("invalid image extension")
        return image
class ConsultantPaymentFom(forms.ModelForm):
    payment_image=forms.ImageField(required=False)
    class Meta:
        model=Cosultant_Payment
        fields=["payment_image","transaction_number"]

    def clean_payment_image(self):
        request=get_current_request()
        image=request.FILES.get("payment_image")
        image_extension=os.path.splitext(image.name)[1]
        if image_extension.lower() not in IMAGE_EXTENSIONS:
            raise forms.ValidationError("invalid image extension")
        return image