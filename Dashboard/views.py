from django.shortcuts import render,redirect
from django.urls import reverse
from Consultant.models import Cosultant_Payment
from home.models import Course,Payment,Events
from Blogs.models import (Blog,Blog_Payment,Blog_Images)
from Quiz.models import *
from django.core.paginator import Paginator
from .forms import *
from accounts.forms import ChangeUserDataForm
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from django.contrib.auth.decorators import user_passes_test
import json
# Create your views here.


@login_required
@check_user_validation
def home(request):
    form=ChangeUserDataForm(request.POST or None,request.FILES or None,instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
    context={"form":form}
    return render(request,"dashboard_home.html",context)


@login_required
@check_user_validation
def blog_payment(request):
    if request.user.account_type == "teacher":
        payments=Blog_Payment.objects.filter(user=request.user).order_by("-id")
    else:
        payments=Blog_Payment.objects.all().order_by("-id")
    paginator = Paginator(payments, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dashboard_blog_payment.html",context)

@login_required
@check_user_validation
def course_payment(request):
    if request.user.account_type == "teacher":
        courses=Payment.objects.filter(user=request.user).order_by("-id")
    else:
        courses=Payment.objects.all().order_by("-id")

    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dashboard_course_payment.html",context)


@login_required
@check_user_validation
def consultant_payment(request):
    if request.user.account_type == "teacher":
        consultant=Cosultant_Payment.objects.filter(user=request.user).order_by("-id")
    else:
        consultant=Cosultant_Payment.objects.all().order_by("-id")
    paginator = Paginator(consultant, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"dashboard_consultant_payment.html",context)

@login_required
@check_user_validation
def blogs(request):
    if request.user.account_type == 'teacher':
        blogs=Blog.objects.filter(user=request.user).order_by("-id")
    else:
        blogs=Blog.objects.all().order_by("-id")
    paginator = Paginator(blogs, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj}
    return render(request,"dashboard_blogs.html",context)

@login_required
@check_user_validation
def courses(request):
    if request.user.account_type == 'teacher':
        courses=Course.objects.filter(Instructor=request.user).order_by("-id")
    else:
        courses=Course.objects.all().order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"courses":page_obj}
    return render(request,"dashboard_course.html",context)
   
@login_required
@check_user_validation
def edit_course(request,slug):
    course=get_object_or_404(Course,slug=slug)
    form=AddCourse(request.POST or None , request.FILES or None,instance=course)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.save()
                messages.success(request,"Course Added Successfully")
                return redirect(reverse("dashboard:courses"))
            else:
                print("invalid")
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:blogs"))
    context={"course":course,"form":form}
    return render(request,"dashboard_course_edit.html",context)

@login_required
@check_user_validation
def add_blog(request):
    form=AddBlog(request.POST or None,request.FILES or None)
    if request.is_ajax():
        blog_type =request.POST["blog_type"]
        if blog_type == "link" or blog_type == "video" or blog_type == "audio":
            blog_type ="link"
        return JsonResponse({"blog_type":blog_type})
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            type=form.cleaned_data.get("blog_type")
            if type == "link" or type == "video" or type == "audio":
                link=request.POST.get("link")
                data={"link":link}
                instance.data=json.dumps(data)
            instance.user=request.user
            instance.save()
            tag=request.POST.get("tags")
            for i in tag.split(","):
                tags,created=Tag.objects.get_or_create(name=i)
                instance.tags.add(tags)
                instance.save()
            image=request.FILES.getlist("image")
            instance.tags.add(tags)
            for i in image:
                image=Blog_Images.objects.create(blog=instance,image=i)
                instance.image.add(image)
                instance.save()
                messages.success(request,"Your Blog is Waiting for Admin Approve")
            return redirect(reverse("dashboard:home"))
        else:
            print("invalid")
    context={"form":form}
    return render(request,"dashboard_add_blog.html",context)


@login_required
@check_user_validation
def edit_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    form=AddBlog(request.POST or None , request.FILES or None,instance=blog)
    if request.user == blog.user:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.save()
                messages.success(request,"Blog Approved Successfully")
                return redirect(reverse("dashboard:blogs"))
            else:
                print("invalid")
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:blogs"))
    context={"blog":blog,"form":form}
    return render(request,"dashboard_edit_blog.html",context)

@login_required
@check_user_validation
def delete_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    if request.user == blog.user:
        blog.delete()
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:blogs"))
    return redirect(reverse("dashboard:blogs"))


@login_required
@check_user_validation
def add_course(request):
    form=AddCourse(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
           instance=form.save(commit=False)
           instance.Instructor=request.user
           instance.save()
           messages.success(request,"course added successfully")
           return redirect(reverse("dashboard:add_video",kwargs={"slug":instance.slug}))
        else:
            print("invalid")
    context={"form":form}
    return render(request,"dashboard_add_course.html",context)

@login_required
@check_user_validation
def add_video(request,slug):
    form=AddVideo(request.POST or None,request.FILES or None)
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.user=request.user
                instance.my_course=course
                instance.save()
                instance.my_course.videos.add(instance)
                instance.my_course.save()
                
                messages.success(request,"Video added successfully")
                form=AddVideo()
            else:
                print("invalid")
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:blogs"))
    context={"form":form}
    return render(request,"dashboard_add_video.html",context)


@login_required
@check_user_validation
def events(request):
    if request.user.account_type == "teacher":
        events=Events.objects.filter(user=request.user).order_by("-id")
    else:
        events=Events.objects.all().order_by("-id")
    context={"events":events}
    return render(request,"dashboard_events.html",context)

@login_required
@check_user_validation
def add_event(request):
    form=AddEvent(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.user=request.user
            instance.save() 
            messages.success(request,"Event added successfully")
            return redirect("dashboard:events")
        else:
            print(request.POST.get("start_time"))
            print('invalid')
    context={"form":form}
    return render(request,"dashboard_add_events.html",context)


@login_required
@check_user_validation
def edit_event(request,id):
    event=get_object_or_404(Events,id=id)
    form=AddEvent(request.POST or None,request.FILES or None,instance=event)
    if request.user == event.user:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.save() 
                messages.success(request,"Event updated successfully")
                return redirect("dashboard:events")
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:events")
    context={"form":form}
    return render(request,"dashboard_add_events.html",context)

@login_required
@check_user_validation
def delete_event(request,id):
    event=get_object_or_404(Events,id=id)
    if request.user == event.user:
        event.delete()
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:events")
    return redirect(reverse("dashboard:events"))

@login_required
@check_user_validation
def quiz(request,slug):
    course=get_object_or_404(Course,slug=slug)
    if request.user.is_director or request.user.is_superuser or request.user == course.Instructor:
        pass
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"quiz":course.quiz,"course":course}
    return render(request,"dashboard_quiz.html",context)


@login_required
@check_user_validation
def add_quiestions(request,slug):
    form=AddQuestion(request.POST or None)
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid(): 
                instance=form.save(commit=False)
                instance.save() 
                if course.quiz == None:
                   quiz=Quiz.objects.create(course_id=course.id)
                   quiz.questions.add(instance)
                   quiz.save()
                   course.quiz=quiz
                   course.save()
                else:
                    course.quiz.questions.add(instance)
                    course.quiz.save()
                messages.success(request,"Question added successfully")
                return redirect(reverse("dashboard:add_answer",kwargs={"course":course.slug,"slug":instance.slug}))
            else:
                print(request.POST.get("start_time"))
                print('invalid')
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_add_question.html",context)

@login_required
@check_user_validation
def edit_quiestions(request,course,slug):
    course=get_object_or_404(Course,slug=course)
    if course.quiz:
        try:
            question=course.quiz.questions.get(slug=slug)
        except:
            messages.error(request,"invalid question")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"invalid question")
        return redirect(reverse("dashboard:courses"))
    form=AddQuestion(request.POST or None,instance=question)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.save() 
                messages.success(request,"Question Edited successfully")
                return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_edit_question.html",context)

@login_required
@check_user_validation
def delete_question(request,slug,id):
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        try:
            course.quiz.questions.get(id=id).delete()
            # if  course.quiz.questions.count() == 0:
                # course.quiz.delete()
                # return redirect(reverse("dashboard:courses"))
        except:
            messages.error(request,"invalid question")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:courses")
    return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))


@login_required
@check_user_validation
def add_answer(request,course,slug):
    form=AddAnswer(request.POST or None)
    course=get_object_or_404(Course,slug=course)
    if course.quiz:
        try:
            question=course.quiz.questions.get(slug=slug)
        except:
            messages.error(request,"invalid question")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"invalid question")
        return redirect(reverse("dashboard:courses"))
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.question=question
                instance.save() 
                question.answer.add(instance)
                course.quiz.answers.add(instance)
                course.quiz.save()
                question.save()
                messages.success(request,"Answer added successfully")
                return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug})) 
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_add_answer.html",context)

@login_required
@check_user_validation
def edit_answer(request,course,id):
    course=get_object_or_404(Course,slug=course)
    if course.quiz:
        try:
            answer=course.quiz.answers.get(id=id)
        except:
            messages.error(request,"invalid answer")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"invalid question")
        return redirect(reverse("dashboard:courses"))
    form=AddAnswer(request.POST or None,instance=answer)
    if request.user == course.Instructor:
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.save() 
                messages.success(request,"Answer Edited successfully")
                return redirect("dashboard:quiz",kwargs={"slug":course.slug})
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:courses"))
    context={"form":form}  
    return render(request,"dashboard_edit_answer.html",context)

@login_required
@check_user_validation
def delete_answer(request,slug,id):
    course=get_object_or_404(Course,slug=slug)
    if request.user == course.Instructor:
        try:
            course.quiz.answers.get(id=id).delete()
            if  course.quiz.questions.count() == 0:
                course.quiz.delete()
        except:
            messages.error(request,"invalid answer")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:courses")
    return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))

