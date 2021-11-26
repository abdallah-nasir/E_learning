from django import forms
from Blogs.models import Blog
from home.models import Course,Branch,Videos,Events
from Quiz.models import Question ,Answers
import os
from crum import get_current_request


class AddBlog(forms.ModelForm):
    image=forms.ImageField(required=True)
    link=forms.HiddenInput()
    class Meta:
        model=Blog
        # exclude=["user","created_at","updated_at","comments","approved"]
        fields=["blog_type","name","details","image","category","paid","tags"]


    def __init__(self,*args,**kwargs):
        super(AddBlog, self).__init__(*args, **kwargs)

        if "blog_type" in self.data:
            type=self.data["blog_type"]
            if type == "link" or type == "video" or type == "audio":
                self.fields["link"] = forms.CharField(required=True)

    # def clean_tags(self):  
    #     request=get_current_request()
    #     tags=request.POST.getlist("tags")
    #     for i in tags:
    #         print(i)
    #     if tags:
    #         raise forms.ValidationError(f"Select only one image for {type} Blog")
    #     return tags
    def clean_blog_type(self):
        request=get_current_request()
        type=self.cleaned_data.get("blog_type")
        image=request.FILES.getlist("image")
        link=request.POST.get("link")
        print(link)
        if type == "link" or type == "video" or type == "audio":
            if not link:
                raise forms.ValidationError("invalid link")
        if type != "gallery":
            if len(image) > 1:  
                raise forms.ValidationError(f"Select only one image for {type} Blog")
        return type

class AddCourse(forms.ModelForm):
    branch=forms.ModelChoiceField(label="Category",queryset=Branch.objects.all())
    # videos=forms.FileField()
    class Meta:
        model=Course
        fields=['name',"image","branch","details","price","course_status"]

class AddVideo(forms.ModelForm):
    class Meta:
        model=Videos

        fields=['name',"video","details"]
from bootstrap_datepicker_plus import DatePickerInput,TimePickerInput,DateTimePickerInput
class AddEvent(forms.ModelForm):
    date=forms.DateField(widget=DatePickerInput(format='%m/%d/%y'))
    start_time=forms.TimeField(widget=TimePickerInput(format='%H:%M:%S'))
    end_time=forms.TimeField(widget=TimePickerInput(format='%I:%M:%S'))
    class Meta:
        model=Events
        fields=['name',"image","details","date","start_time","end_time","place"]

class AddQuestion(forms.ModelForm):
    class Meta:
        model=Question
        fields=["title","details"]

class AddAnswer(forms.ModelForm):
    class Meta:
        model=Answers
        fields=["answer","correct"]