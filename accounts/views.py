from django.shortcuts import render,redirect,reverse
import os
from django.contrib.auth import logout 
from django.contrib import messages
from .forms import *
from .models import TeacherForms
from .models import User
from .decorators import check_user_is_student
from home.models import *
from Blogs.models import *
from Consultant.models import Consultant, Cosultant_Payment
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import json,requests 
from .utils import *
from .forms import MyCustomLoginForm,MyCustomSignupForm
from allauth.account.views import SignupView,LoginView
# from allauth.account.forms import LoginForm,SignupForm
Storage_Api=os.environ["Storage_Api"]
storage_name=os.environ["storage_name"]
  
# Create your views here.

class CustomSignupView(SignupView):
    # here we add some context to the already existing context
    def get_context_data(self, **kwargs):
        # we get context data from original view
        context = super(SignupView,
                        self).get_context_data(**kwargs)
        context['login_form']=MyCustomLoginForm() # add form to context

        if self.request.GET.get("next"):
               context.update({"redirect_field_name":self.redirect_field_name,
            "redirect_field_value":get_request_param(self.request, self.redirect_field_name)
})
      
        return context

class CustomSigninView(LoginView):
    # here we add some context to the already existing context
   
    def get_context_data(self, **kwargs):
        # we get context data from original view
        context = super(LoginView,
                        self).get_context_data(**kwargs)
      
        if self.request.GET.get("next"):
               context.update({"redirect_field_name":self.redirect_field_name,
            "redirect_field_value":get_request_param(self.request, self.redirect_field_name)
})
        context.update({'signup_form': MyCustomSignupForm()}) # add form to context   
        return context  

        
def logout_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse("home:home"))
    else:
        logout(request)
        messages.success(request,"you have logged out")
        return redirect(reverse("home:home"))


from django.contrib.sites.models import Site

def random_string_generator(size=7, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url="accounts:login")
@check_user_is_student
def check_teacher_form(request):
    teacher_form=TeacherForms.objects.filter(teacher=request.user)
    if teacher_form.exists():
        teacher=teacher_form[0]
        if teacher.status == "declined":
            form=Teacher_Form(request.POST or None,instance=teacher)
            data=json.loads(teacher.data)
            form.initial["title"]=data["title"]
            form.initial["about_me"]=data["about_me"]
            form.initial["facebook"]=data["social"][0]["facebook"]
            form.initial["linkedin"]=data["social"][0]["linkedin"]
            form.initial["twitter"]=data["social"][0]["twitter"]

        else:
            form=Teacher_Form(request.POST or None)
    else:
        form=Teacher_Form(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():  
            if teacher_form.exists():
                if teacher_form[0].status == "pending" or teacher_form[0].status == "approved":
                    messages.error(request,"your already have a Form")
                    form=Teacher_Form()
                    return redirect(reverse("accounts:account_info"))
            instance=form.save(commit=False)
            facebook=form.cleaned_data['facebook']
            linkedin=form.cleaned_data['linkedin']
            twitter=form.cleaned_data['twitter']
            about_me=form.cleaned_data['about_me']
            title=form.cleaned_data['title']
            data={"social":[{"facebook":facebook,"linkedin":linkedin,"twitter":twitter}],
            "about_me":about_me,"title":title}
            instance.teacher=request.user
            instance.data=json.dumps(data)
            instance.status="pending"
            instance.save()
            messages.success(request,"your request is being review by admins")
            return redirect(reverse("accounts:account_info"))
    context={"form":form}
    return render(request,"check_teacher.html",context)

@login_required(login_url="accounts:login")
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

@login_required(login_url="accounts:login")
def blog_payment(request):
    payments=Blog_Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(payments, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_blog_payment.html",context)

@login_required(login_url="accounts:login")
def course_payment(request):
    courses=Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_course_payment.html",context)


@login_required(login_url="accounts:login")
def consultant_payment(request):
    consultant=Cosultant_Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(consultant, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_consultant_payment.html",context)

# @login_required(login_url="accounts:login")
# def blogs(request):
#     blogs=Blog.objects.filter(user=request.user).order_by("-id")
#     paginator = Paginator(blogs, 10) # Show 25 contacts per page.
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context={"blogs":page_obj}
#     return render(request,"account_blogs.html",context)

@login_required(login_url="accounts:login")
def courses(request):
    courses=Course.objects.filter(students=request.user).order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"courses":page_obj}
    return render(request,"account_course.html",context)

@login_required(login_url="accounts:login")
def events(request):
    events=Events.objects.filter(students=request.user).order_by("-id")
    paginator = Paginator(events, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"events":page_obj}
    return render(request,"account_events.html",context)

@login_required(login_url="accounts:login")
def consultants(request):
    consult=Consultant.objects.filter(Q(user=request.user,status="approved") | Q(user=request.user,status="completed")).order_by("-id")
    paginator = Paginator(consult, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"consult":page_obj}
    return render(request,"account_consult.html",context)

@login_required(login_url="accounts:login")
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

@login_required(login_url="accounts:login")
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

@login_required(login_url="accounts:login")
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

 
def code_reset(request):
    form=CodeForm(request.POST or None)
    if request.method =="POST":
        if form.is_valid():
            email=form.cleaned_data.get("email")
            user=User.objects.filter(email=email)
            if user:
                this_user=user.last()
                if this_user.is_active == True:
                    messages.error(request,"your account is active")
                else:
                    this_user.code=random_string_generator()
                    this_user.save()
                    msg = EmailMessage(subject="Account Created", body=f"code:{this_user.code} \n url:{request.scheme}://{request.META['HTTP_HOST']}/profile/validate/teacher/", from_email=settings.EMAIL_HOST_USER, to=[this_user.email])
                    msg.content_subtype = "html"  # Main content is now text/html
                    msg.send()
                    messages.success(request,"code has been sent to your email")
            else:
                messages.error(request,"invalid user")
        form=CodeForm()
    context={"form":form}
    return render(request,"account_code.html",context)