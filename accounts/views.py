from django.shortcuts import render,redirect,reverse
from django.contrib.auth import logout 
from django.contrib import messages
from .forms import *
from .models import TeacherForms
from .models import User
from home.models import *
from Blogs.models import *
from Consultant.models import Consultant, Cosultant_Payment
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import json,requests 
Storage_Api="b6a987b0-5a2c-4344-9c8099705200-890f-461b"
storage_name="agartha"

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
    form.initial["account_image"]=None
    if request.method == 'POST':
        if form.is_valid():     
            instance=form.save(commit=False)
            try:
                if request.FILES["account_image"]:
                    print(request.FILES["account_image"])
                    file_name=request.FILES["account_image"]
                    url=f"https://storage.bunnycdn.com/{storage_name}/accounts/{instance.slug}/"
                    headers = {
                        "Accept": "*/*", 
                        "AccessKey":Storage_Api}
                    response = requests.get(url, headers=headers) 
                    data=response.json()
                    for i in data:
                        url=f"https://storage.bunnycdn.com/{storage_name}/accounts/{instance.slug}/{i['ObjectName']}"
                        response = requests.delete(url,headers=headers)
                    url=f"https://storage.bunnycdn.com/{storage_name}/accounts/{instance.slug}/{file_name}"
                    file=form.cleaned_data.get("account_image")
                    response = requests.put(url,data=file,headers=headers)
                    data=response.json()
                    try:
                        if data["HttpCode"] == 201:
                            instance.account_image = f"https://{agartha_cdn}/accounts/{instance.slug}/{file_name}"
                            instance.save()
                    except:
                        pass
            except:
                pass
            instance.save()
            form=ChangeUserDataForm(instance=request.user)
            form.initial["account_image"]=None
            messages.success(request,"Profile Updated Successfully")
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
def consultants(request):
    consult=Consultant.objects.filter(Q(user=request.user,status="approved") | Q(user=request.user,status="completed")).order_by("-id")
    paginator = Paginator(consult, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"consult":page_obj}
    return render(request,"account_consult.html",context)

@login_required
def edit_blog_payment(request,id):
    payment=get_object_or_404(Blog_Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Paypal":
            messages.error(request,"You Can't Edit Paypal Payment")
            return redirect(reverse("accounts:blog_payment"))
        form=BlogPaymentFom(request.POST or None,request.FILES or None,instance=payment)
        form.initial["payment_image"]=None
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.status="pending"
                image=request.FILES["payment_image"]
                url=f"https://storage.bunnycdn.com/{storage_name}/blog-payment/{instance.user.slug}/{image}"
                headers = {
                    "Content-Type": "application/octet-stream",
                    "AccessKey": Storage_Api
                }
                response = requests.put(url,data=image,headers=headers)
                data=response.json()
                try: 
                    if data["HttpCode"] == 201:
                        instance.payment_image = f"https://{agartha_cdn}/blog-payment/{instance.user.slug}/{image}"
                        instance.save()
                except:
                    pass                 
                instance.save()
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
        form.initial["payment_image"]=None
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.status="pending"
                image=request.FILES["payment_image"]
                url=f"https://storage.bunnycdn.com/{storage_name}/course-payment/{instance.course.slug}/{image}"
                headers = {
                    "Content-Type": "application/octet-stream",
                    "AccessKey": Storage_Api
                }
                response = requests.put(url,data=image,headers=headers)
                data=response.json()
                try: 
                    if data["HttpCode"] == 201:
                        instance.payment_image = f"https://{agartha_cdn}/course-payment/{instance.course.slug}/{image}"
                        instance.save()
                except:
                    pass                 
                instance.save()
                messages.success(request,"Payment Edited Successfully")
                return redirect(reverse("accounts:course_payment"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("accounts:course_payment"))
    context={"form":form,"payment":payment} 
    return render(request,"edit_course_payment.html",context)

@login_required
def edit_consultant_payment(request,id):
    payment=get_object_or_404(Cosultant_Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Paypal":
            messages.error(request,"You Can't Edit Paypal Payment")
            return redirect(reverse("accounts:consultant_payment"))
        form=ConsultantPaymentFom(request.POST or None,request.FILES or None,instance=payment)
        form.initial["payment_image"]=None
        if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                instance.status="pending"
                image=request.FILES["payment_image"]
                url=f"https://storage.bunnycdn.com/{storage_name}/consultant-payment/{instance.user.slug}/{instance.consult.teacher.date}/{image}"
                headers = {
                    "Content-Type": "application/octet-stream",
                    "AccessKey": Storage_Api
                }
                response = requests.put(url,data=image,headers=headers)
                data=response.json()
                try: 
                    if data["HttpCode"] == 201:
                        instance.payment_image = f"https://{agartha_cdn}/consultant-payment/{instance.user.slug}/{instance.consult.teacher.date}/{image}"
                        instance.save()
                except:
                    pass                 
                instance.save()
                messages.success(request,"Payment Edited Successfully")
                return redirect(reverse("accounts:consultant_payment"))
    else:
        messages.error(request,"You Don't Have Permission")
        return redirect(reverse("accounts:consultant_payment"))
    context={"form":form}
    return render(request,"edit_consultant_payment.html",context)
