from django.shortcuts import render,redirect
from django.template.defaultfilters import urlencode
from django.urls import reverse
from Consultant.models import Cosultant_Payment,Consultant,Teacher_Time
from home.models import Course,Payment,Events,Videos,News
from Blogs.models import (Blog,Blog_Payment,Blog_Images)
from Quiz.models import *
from accounts.models import TeacherForms
from django.core.paginator import Paginator
from .forms import *
from django.core.mail import send_mail,send_mass_mail

from django.conf import settings
from accounts.forms import ChangeUserDataForm
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from .models import *
from django.contrib.auth.decorators import user_passes_test
import json
from django.contrib.auth import get_user_model
User=get_user_model()
urlencode
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
@check_if_user_director
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
@check_if_user_director
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
@check_if_user_director
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
def add_blog(request):
    blog_type_list=["standard","gallery","video","audio","quote","link"]
    try:
        type=request.GET["blog_type"]
        if type not in blog_type_list:
            return redirect(reverse("dashboard:blogs"))
        elif type == "link":
            form=BlogLinkForm(request.POST or None,request.FILES or None)
        elif type == "quote":
            form=BlogQuoteForm(request.POST or None,request.FILES or None)
        elif type == "video" or type == "audio":
            form=BlogVideoForm(request.POST or None,request.FILES or None)
        elif type == 'gallery':
            form=BlogGalleryForm(request.POST or None,request.FILES or None)
        else:
            form=AddBlog(request.POST or None,request.FILES or None)
        form_number=1
    except:
        form=BlogTypeForm(request.GET or None)
        form_number=2
    if request.method == "POST":
        if form_number == 1:
            if form.is_valid():
                instance=form.save(commit=False)
                if type == "link":
                    link=request.POST.get("link")
                    data={"link":link}
                    instance.data=json.dumps(data)
                if type == "quote":
                    quote=request.POST.get("quote")
                    data={"quote":quote}
                    instance.data=json.dumps(data)
                instance.user=request.user
                instance.blog_type = type
                instance.save()
                tag=request.POST.get("tags")
                print(tag)
                if tag:
                    for i in tag.split(","):
                        tags,created=Tag.objects.get_or_create(name=i)
                        instance.tags.add(tags)
                        instance.save()
                image=request.FILES.getlist("image")
                for i in image:
                    image=Blog_Images.objects.create(blog=instance,image=i)
                    instance.image.add(image)
                    instance.save()
                messages.success(request,"Your Blog is Waiting for Admin Approve")
                return redirect(reverse("dashboard:blogs"))

    context={"form":form,"form_number":form_number}
    return render(request,"dashboard_add_blog.html",context)


@login_required
@check_user_validation
def edit_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug,status="declined")
    blog_type_list=["standard","gallery","video","audio","quote","link"]
    try:
        type=request.GET["blog_type"]
        if type not in blog_type_list:
            return redirect(reverse("dashboard:blogs"))
        elif type == "link":
            form=BlogLinkForm(request.POST or None,request.FILES or None,instance=blog)
            form.initial["link"] = blog.get_link()
        elif type == "quote":
            form=BlogQuoteForm(request.POST or None,request.FILES or None,instance=blog)
            form.initial["quote"]=blog.get_quote()
        elif type == "video" or type == "audio":
            form=BlogVideoForm(request.POST or None,request.FILES or None,instance=blog)
        elif type == 'gallery':
            form=BlogGalleryForm(request.POST or None,request.FILES or None,instance=blog)
        else:
            form=AddBlog(request.POST or None,request.FILES or None,instance=blog)
        form_number=1
    except: 
        form=BlogTypeForm(request.GET or None,instance=blog)
  
        form_number=2
    if request.user == blog.user:
        if request.method == "POST":
            Rejects.objects.filter(user=request.user,type="blogs",content_id=blog.id).delete()
            if form_number == 1:
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.approved=False
                    type=request.GET["blog_type"]
                    if type == "link":
                        link=request.POST.get("link")
                        data={"link":link}
                        instance.data=json.dumps(data)
                    if type == "quote":
                        quote=request.POST.get("quote")
                        data={"quote":quote}
                        instance.data=json.dumps(data)
                    instance.blog_type=type
                    tag=form.cleaned_data.get("tags")
                    tag_list=[]
                    if tag:
                        for i in tag:
                            tag_list.append(i)
                            if i in blog.tags.all():
                                pass
                            else:
                                new_tags,created=Tag.objects.get_or_create(name=i)
                                instance.tags.add(new_tags)
                                instance.save()
                        for i in instance.tags.all():
                            if i.name in tag_list:
                                pass
                            else:
                                instance.tags.remove(i)
                    image=request.FILES.getlist("image")
                    if image != []:
                        if type != "gallery":
                            this_image=image[-1]
                            if len(blog.image.all()) > 1:
                                blog.image.all().delete()
                                image=Blog_Images.objects.create(blog=instance,image=this_image)
                                instance.image.add(image)
                                instance.save()
                            elif blog.image.last() != this_image:

                                blog.image.all().delete()
                                image=Blog_Images.objects.create(blog=instance,image=this_image)
                                instance.image.add(image)
                                instance.save()
                        else:
                            for i in image:
                                image=Blog_Images.objects.create(blog=instance,image=i)
                                instance.image.add(image)
                                instance.save()
                    if type == "audio" or type == "video":
                        video_audio=form.cleaned_data.get("video")
                        instance.video=video_audio
                        instance.save()
                    else:
                        if blog.video:
                            blog.video.delete()
                    instance.status="pending"
                    instance.save()
                    messages.success(request,"Your Blog is Waiting for Admin Approve")
                    return redirect(reverse("dashboard:blogs"))
    else:
        messages.error(request,"You Don't Have Permisssion")
        return redirect(reverse("dashboard:blogs"))
    context={"blog":blog,"form":form,"form_number":form_number}
    return render(request,"dashboard_edit_blog.html",context)

@login_required
@check_user_validation
def delete_blog_image(request,id):
    image=get_object_or_404(Blog_Images,id=id)
    if image.blog.user == request.user:
        image.delete()
    return redirect(reverse("dashboard:edit_blog",kwargs={"slug":image.blog.slug}))

@login_required
@check_user_validation
def delete_blog_video(request,id):
    blog=get_object_or_404(Blog,id=id)
    if blog.user == request.user:
        blog.video.delete()
    return redirect(reverse("dashboard:edit_blog",kwargs={"slug":blog.slug}))

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
            Rejects.objects.filter(user=request.user,type="course",content_id=course.id).delete()

            if form.is_valid():
                instance=form.save(commit=False)
                instance.save()
                messages.success(request,"Course Edited Successfully")
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
def videos(request):
    if request.user.account_type == "teacher":
        videos=Videos.objects.filter(user=request.user).order_by("-id")
    else:
        videos=Videos.objects.all().order_by("-id")
    context={"videos":videos}
    return render(request,"dashboard_videos.html",context)

@login_required
@check_user_validation
def delete_videos(request,slug):
    video=get_object_or_404(Videos,slug=slug)
    if request.user == video.user:
        video.delete()
        video.total_duration()
        return redirect(reverse("dashboard:videos"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:home"))

@login_required
@check_user_validation
def edit_videos(request,slug):
    video=get_object_or_404(Videos,slug=slug,my_course__status="approved")
    if request.user == video.user:
        form=EditVideo(request.POST or None,request.FILES or None,instance=video)
        if request.method == "POST":
            instance=form.save(commit=False)
            # if request.FILES.get("video") != None:
            #     video.video.delete()
            #     instance.video=request.FILES.get("video") 
                # print("here")     
            instance.save()
            messages.success(request,"video edited successfully")
            return redirect(reverse("dashboard:videos"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("dashboard:home"))
    context={"form":form}
    return render(request,"dashboard_edit_video.html",context)

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
@check_if_teacher_has_event
def add_event(request):
    form=AddEvent(request.POST or None,request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            instance.user=request.user
            zoom=form.cleaned_data.get("zoom_link")
            details=form.cleaned_data.get("details")
            data={'zoom':zoom,"details":details}
            instance.details=json.dumps(data)  
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
    event=get_object_or_404(Events,id=id,status="declined")
    form=AddEvent(request.POST or None,request.FILES or None,instance=event)
    form.initial["details"]=event.get_details()["details"]
    form.initial["zoom_link"]=event.get_details()["zoom"]
    if request.user == event.user:
        if request.method == "POST":
            Rejects.objects.filter(user=request.user,type="events",content_id=id).delete()

            if form.is_valid():
                instance=form.save(commit=False)
                zoom=form.cleaned_data.get("zoom_link")
                details=form.cleaned_data.get("details")
                data={'zoom':zoom,"details":details}
                instance.details=json.dumps(data)  
                instance.status="pending"
                instance.get_similar_event()
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
def finish_event(request,id):
    event=get_object_or_404(Events,id=id)
    if request.user == event.user:
        event.status = "completed"
        event.save()
        messages.success(request,"Event End Successfully")
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:events")
    return redirect(reverse("dashboard:events"))
@login_required
@check_user_validation
def start_event(request,slug):
    event=get_object_or_404(Events,slug=slug,status="approved")
    if request.user == event.user:
        emails=event.get_students_events()
        # html="dashboard_events.html"

        event.status="start"
        event.save()
        messages.success(request,"Event Has Been Started")
    else:
        messages.error(request,"invalid event status")
        return redirect(reverse("dashboard:events"))
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
                   course.course_status = "on process"
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
                course.course_status = "on process"
                course.save()
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
                course.course_status = "on process"
                course.save()
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
                course.course_status = "on process"
                course.save()
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
            # if  course.quiz.questions.count() == 0:
            #     course.quiz.delete()
        except:
            messages.error(request,"invalid answer")
            return redirect(reverse("dashboard:courses"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect("dashboard:courses")
    return redirect(reverse("dashboard:quiz",kwargs={"slug":course.slug}))

@login_required
@check_user_validation
def teachers(request):
    if request.user.is_superuser or request.user.is_director:
        teacher=User.objects.filter(account_type="teacher").order_by("-id")
        paginator = Paginator(teacher, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        messages.error(request,"You Don't have Permission")
        return redirect(reverse("dashboard:home"))
    context={"teachers":page_obj}
    return render(request,"dashboard_teachers.html",context)

def get_choices_keys():
    choices={"Blogs":"blogs","Consultant Payment":"consultant_payment"}
    for i in choices.values():
        print(i)
    return True

@login_required
def approve(request):
    if request.user.is_superuser :
        try:
            qs=request.GET["approve"]
            choices={"Teachers":"teacher","Blogs":"blogs","Blog Payments":"blog_payment","Consultant Payment":"consultant_payment",
                "Course":"course","Course Payments":"payment","Events":"events"}
            if qs == "blogs":
                query=Blog.objects.filter(status="pending").order_by("-id")
            elif qs == "blog_payment":  
                query=Blog_Payment.objects.filter(status="pending").order_by("-id")
            elif qs == "consultant_payment": 
                query=Cosultant_Payment.objects.filter(status="pending").order_by("-id")
            elif qs == "course":
                query=Course.objects.filter(status="pending").order_by("-id")
            elif qs == "events":
                query=Events.objects.filter(status="pending").order_by("-id")
            elif qs == "payment":
                query=Payment.objects.filter(status="pending").order_by("-id")
            elif qs == "teacher":
                query=TeacherForms.check_reject.get_query_set().order_by("-id")
            else:
                query=False
        except:
            return redirect(reverse("dashboard:home"))

    else:
        messages.error(request,"You Don't have Permission")
        return redirect(reverse("dashboard:home"))
    context={"query":query,"qs":qs,"choices":choices}
    return render(request,"dashboard_approve.html",context)

@login_required
def show_demo_blog(request,slug):
    if request.user.is_superuser :
        blog=get_object_or_404(Blog,status="pending",slug=slug)
    else:
        messages.error(request,"You Don't Have permission")
        return redirect(reverse("home:home"))
    context={"blog":blog}
    return render(request,"dashboard_show_demo_blog.html",context)

@login_required
def approve_content(request,id):
    if request.user.is_superuser:
        try:
            qs=request.GET["approve"]

            if qs == "blogs":
                query=get_object_or_404(Blog,id=id,status="pending")
                query.status="approved"
                query.save()
                messages.success(request,"Blog Approved Successfully")
            elif qs == "blog_payment":
                query=get_object_or_404(Blog_Payment,id=id,status="pending")
                query.status="approved"
                query.save()
                query.user.vip = True
                query.user.save()
                messages.success(request,"Payment Approved Successfully")
            elif qs == "consultant_payment":
                query=get_object_or_404(Cosultant_Payment,id=id,status="pending")
                query.status="approved"
                query.consult.status="approved"
                query.save()
                query.consult.save()
                messages.success(request,"Payment Approved Successfully")
            elif qs == "course":
                query=get_object_or_404(Course,id=id,status="pending")
                query.status="approved"
                query.save()
                messages.success(request,"Course Approved Successfully")
            elif qs == "events":
                query=get_object_or_404(Events,id=id,status="pending")
                query.status="approved"
                query.save()
                messages.success(request,"Event Approved Successfully")
            elif qs == "payment":
                query=get_object_or_404(Payment,id=id,status="pending")
                query.status="approved"
                query.course.students.add(query.user)
                query.course.save()
                query.save()
                messages.success(request,"Payment Approved Successfully")
            elif qs == "teacher":
                query=get_object_or_404(TeacherForms,id=id,approved=False)
                query.approved=True
                query.teacher.is_active=True
                query.teacher.save()
                query.save()
                messages.success(request,"Teacher Approved Successfully")
        except:
            return redirect(reverse("dashboard:home"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("home:home"))
    redirect_url = reverse('dashboard:approve')

    # parameters = urlencode()
    return redirect(f'{redirect_url}?approve={qs}') 

@login_required
def reject(request,id):
    if request.user.is_superuser:
        try:
            qs=request.GET["reject"]
            content=Rejects.objects.filter(type=qs,content_id=id)
            if content.exists():
                messages.error(request,"Form is ALready Rejected")
                redirect_url = reverse('dashboard:approve')
                return redirect(f'{redirect_url}?approve={qs}') 
            elif qs == "blogs":
                query=get_object_or_404(Blog,id=id,status="pending")
                content_user=query.user
            elif qs == "blog_payment":
                query=get_object_or_404(Blog_Payment,id=id,status="pending")
                content_user=query.user
            elif qs == "consultant_payment":
                query=get_object_or_404(Cosultant_Payment,id=id,status="pending")
                content_user=query.user
            elif qs == "course":
                query=get_object_or_404(Course,id=id,status="pending")
                content_user=query.Instructor
            elif qs == "events":
                query=get_object_or_404(Events,id=id,status="pending")
                content_user=query.user
            elif qs == "payment":
                query=get_object_or_404(Payment,id=id,status="pending")
                content_user=query.user
            elif qs == "teacher":
                query=get_object_or_404(TeacherForms,id=id,approved=False)
                content_user=query.teacher
            form=RejectForm(request.POST or None)
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    print(form.cleaned_data.get("message"))
                    instance.type=qs
                    instance.user=content_user
                    instance.content_id=id
                    instance.save()
                    # send_mail(
                    #     form.cleaned_data.get("subject"),
                    #     form.cleaned_data.get("message"),
                    #     settings.EMAIL_HOST_USER,
                    #     [content_user.email],
                    #     fail_silently=False,
                    #     )
                    if qs == "teacher":
                        query.delete()
                    else:
                        query.status="declined"
                        query.save()
                    # if qs == "teacher":
                    #     print("teacher")
                        # query.delete()
                    messages.success(request,"Content Rejected Successfully")
                    redirect_url = reverse('dashboard:approve')
                    return redirect(f'{redirect_url}?approve={qs}') 
        except:
          
            return redirect(reverse("dashboard:home"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("home:home"))
    context={"form":form,"query":query,"qs":qs}
    return render(request,"dashboard_reject_form.html",context)

@login_required
def news(request):
    if request.user.is_superuser or request.user.is_director:
        news=News.objects.all().order_by("-id")
        paginator = Paginator(news, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context={"news":page_obj}
    else:
        messages.error(request,"You Don't have Permission")
        return redirect(reverse("dashboard:home"))
    return render(request,"dashboard_news.html",context)

@login_required
@admin_director_check
def delete_news(request,id):
    news=get_object_or_404(News,id=id)
    news.delete()
    messages.success(request,"News Deleted Successfully")
    return redirect(reverse("dashboard:news"))

@login_required
@admin_director_check
def edit_news(request,id):
    news=get_object_or_404(News,id=id)
    form=NewsForm(request.POST or None,instance=news)
    if request.method == "POST":
        instance=form.save(commit=False)
        instance.save()
        messages.success(request,"News Edited Successfully")
        return redirect(reverse("dashboard:news"))
    context={"form":form}
    return render(request,"dashboard_edit_news.html",context)

@login_required
@admin_director_check
def add_news(request):
    form=NewsForm(request.POST or None)
    if request.method == "POST":
        instance=form.save(commit=False)
        instance.save()
        messages.success(request,"News Added Successfully")
        return redirect(reverse("dashboard:news"))
    context={"form":form}
    return render(request,"dashboard_add_news.html",context)

@login_required
@check_user_validation
def consultants(request):
    if request.user.account_type == "teacher":
        consultants=Consultant.objects.filter(user=request.user,status="approved").order_by("-id")
    else:
        consultants=Consultant.objects.all()
    paginator = Paginator(consultants, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"consultants":consultants}
    return render(request,"dashboard_consultants.html",context)

@login_required
@check_user_validation
def consultants_sessions(request):
    if request.user.account_type == "teacher":
        sessions=Teacher_Time.objects.filter(user=request.user).order_by("-id")
    else:
        sessions=Teacher_Time.objects.all().order_by("-id")

    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"sessions":sessions}
    return render(request,"dashboard_consultants_sessions.html",context)

@login_required
@check_user_validation
@check_if_teacher_have_consultants
def add_consultant(request):
    form=CosultantAddForm(request.POST or None)
    if request.method == "POST":
        instance=form.save(commit=False)
        instance.user=request.user
        instance.save()
        messages.success(request,"Consultant Added Successfully")
        return redirect(reverse("dashboard:consultants_sessions"))
    context={"form":form}
    return render(request,"dashboard_add_consultant.html",context)

@login_required
@check_user_validation
def complete_consultant(request,id):
    consult=get_object_or_404(Consultant,id=id,status="approved")
    if request.user == consult.teacher.user:
        consult.status="completed"
        consult.save()
        messages.success(request,"Consultant Completed Successfully")
    return redirect(reverse("dashboard:consultants"))