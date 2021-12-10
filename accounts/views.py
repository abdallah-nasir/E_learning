from django.shortcuts import render,redirect,reverse
from django.contrib.auth import logout 
from django.contrib import messages
from .forms import *
from .models import TeacherForms
from .models import User
from home.models import *
from Blogs.models import *
from Consultant.models import Cosultant_Payment
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import json
# Create your views here.


def logout_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse("home:home"))
    else:
        logout(request)
        messages.success(request,"you have logged out")
        return redirect(reverse("home:home"))

def check_teacher_form(request):
    form=Teacher_Form(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                teacher_username=form.cleaned_data["username"]
                user=User.objects.get(Q(username=teacher_username) | Q(email=teacher_username))
                teacher_form=TeacherForms.objects.filter(teacher=user,approved=False)
                if teacher_form.exists() and user.is_active == False:
                    messages.error(request,"your already have a Form")
                    form=Teacher_Form()
                else: 
                    facebook=form.cleaned_data['facebook']
                    linkedin=form.cleaned_data['linkedin']
                    twitter=form.cleaned_data['twitter']
                    about_me=form.cleaned_data['about_me']
                    title=form.cleaned_data['title']
                    code=form.cleaned_data['code']
                    data={"social":[{"facebook":facebook,"linkedin":linkedin,"twitter":twitter}],
                        "about_me":about_me,"title":title}
                    if code == user.code:
                        new_teacher=TeacherForms.objects.create(teacher=user,data=json.dumps(data),code=code,approved=False)
                        user.my_data=new_teacher.data
                        user.save()
                        messages.success(request,"your request is being review by admins")
                        form=Teacher_Form()
                    else:
                        messages.error(request,f"invalid code for user {user.username}")
            except:
                messages.error(request,"invalid data")
                form=Teacher_Form()
    context={"form":form}
    return render(request,"check_teacher.html",context)

@login_required
def account_info(request):
    form=ChangeUserDataForm(request.POST or None,request.FILES or None,instance=request.user)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.save()
        messages.success(request,"Account Updated Successfully")
        form=ChangeUserDataForm(instance=request.user)
    context={"form":form} 
    return render(request,"account_user_info.html",context)

@login_required
def blog_payment(request):
    payments=Blog_Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(payments, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_blog_payment.html",context)

@login_required
def course_payment(request):
    courses=Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_course_payment.html",context)


@login_required
def consultant_payment(request):
    consultant=Cosultant_Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(consultant, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_consultant_payment.html",context)

# @login_required
# def blogs(request):
#     blogs=Blog.objects.filter(user=request.user).order_by("-id")
#     paginator = Paginator(blogs, 10) # Show 25 contacts per page.
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context={"blogs":page_obj}
#     return render(request,"account_blogs.html",context)

@login_required
def courses(request):
    courses=Course.objects.filter(students=request.user).order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"courses":page_obj}
    return render(request,"account_course.html",context)

@login_required
def events(request):
    events=Events.objects.filter(students=request.user).order_by("-id")
    paginator = Paginator(events, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"events":page_obj}
    return render(request,"account_events.html",context)


@login_required
def edit_blog_payment(request,id):
    payment=get_object_or_404(Blog_Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Paypal":
            messages.error(request,"You Can't Edit Paypal Payment")
            return redirect(reverse("accounts:blog_payment"))
        form=BlogPaymentFom(request.POST or None,request.FILES or None,instance=payment)

        if request.method == "POST":
            if form.is_valid():
                instance=form.save()
                messages.success(request,"Payment Edited Successfully")
                return redirect(reverse("accounts:blog_payment"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("accounts:blog_payment"))
    context={"form":form}
    return render(request,"edit_blog_payment.html",context)

@login_required
def edit_course_payment(request,id):
    payment=get_object_or_404(Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Paypal":
            messages.error(request,"You Can't Edit Paypal Payment")
            return redirect(reverse("accounts:course_payment"))
        form=CoursePaymentFom(request.POST or None,request.FILES or None,instance=payment)

        if request.method == "POST":
            if form.is_valid():
                instance=form.save()
                messages.success(request,"Payment Edited Successfully")
                return redirect(reverse("accounts:course_payment"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("accounts:course_payment"))
    context={"form":form}
    return render(request,"edit_course_payment.html",context)

@login_required
def edit_consultant_payment(request,id):
    payment=get_object_or_404(Cosultant_Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Paypal":
            messages.error(request,"You Can't Edit Paypal Payment")
            return redirect(reverse("accounts:consultant_payment"))
        form=BlogPaymentFom(request.POST or None,request.FILES or None,instance=payment)

        if request.method == "POST":
            if form.is_valid():
                instance=form.save()
                messages.success(request,"Payment Edited Successfully")
                return redirect(reverse("accounts:consultant_payment"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("accounts:consultant_payment"))
    context={"form":form}
    return render(request,"edit_consultant_payment.html",context)
