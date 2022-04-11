from django.shortcuts import render,redirect
import os
from django.contrib.auth import logout 
from django.contrib import messages
from django.urls import reverse
from .forms import *
from .models import TeacherForms
from .models import User
from .kemet_decorators import *
from home.models import * 
from Blogs.models import *
from Consultant.models import Consultant, Cosultant_Payment
from django.core.paginator import Paginator
from library.models import Library_Payment,Movies
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import json,requests 
from django.shortcuts import get_object_or_404
from .utils import *
from .forms import MyCustomLoginForm,MyCustomSignupForm
from allauth.account.views import SignupView,LoginView
from Dashboard import models as dahboard_models
from django.core.mail import EmailMessage,get_connection
from E_learning.all_email import *

# from allauth.account.forms import LoginForm,SignupForm
Storage_Api=os.environ["Storage_Api"]
storage_name=os.environ["storage_name"]
agartha_cdn=os.environ['agartha_cdn']

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
            body=f"teacher join request from {request.user.email}"
            subject="teacher join"
            send_mail_approve(request,user=request.user.email,subject=subject,body=body)
            return redirect(reverse("accounts:account_info"))
    context={"form":form}
    return render(request,"kemet/check_teacher.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher
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
@redirect_teacher_blog_payment
def blog_payment(request):
    payments=Blog_Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(payments, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_blog_payment.html",context)

@login_required(login_url="accounts:login")
@redirect_teacher_course_payment
def course_payment(request):
    courses=Payment.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_course_payment.html",context)


@login_required(login_url="accounts:login")
@redirect_teacher_consultant_payment
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
@redirect_teacher_movies_payment
def movies_payment(request):
    movies=Library_Payment.objects.filter(user=request.user,library_type=3).order_by("-id")
    paginator = Paginator(movies, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_movies_payment.html",context)

@login_required(login_url="accounts:login")
@redirect_teacher_audio_payment
def audio_payment(request):
    movies=Library_Payment.objects.filter(user=request.user,library_type=2).order_by("-id")
    paginator = Paginator(movies, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_audio_payment.html",context)

@login_required(login_url="accounts:login")
@redirect_audio_book_payment
def audio_book_payment(request):
    movies=Library_Payment.objects.filter(user=request.user,library_type=1).order_by("-id")
    paginator = Paginator(movies, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"payments":page_obj}
    return render(request,"account_audio_book_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher
def courses(request):
    courses=Course.objects.filter(students=request.user).order_by("-id")
    paginator = Paginator(courses, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"courses":page_obj}
    return render(request,"account_course.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher
def events(request):
    events=Events.objects.filter(students=request.user).order_by("-id")
    paginator = Paginator(events, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"events":page_obj}
    return render(request,"account_events.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher
def consultants(request):
    consult=Consultant.objects.filter(Q(user=request.user,status="approved") | Q(user=request.user,status="completed")).order_by("-id")
    paginator = Paginator(consult, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"consult":page_obj}
    return render(request,"account_consult.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher 
@check_edit_blog_pyment
def edit_blog_payment(request,id):
    payment=get_object_or_404(Blog_Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            form=BlogPaymentFom(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
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
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:blog_payment"))
        else:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:blog_payment"))
    context={"form":form}
    return render(request,"edit_blog_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher
@check_edit_course_pyment
def edit_course_payment(request,id):
    payment=get_object_or_404(Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            form=CoursePaymentFom(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
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
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:course_payment"))
        else:
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:course_payment"))
    context={"form":form,"payment":payment} 
    return render(request,"edit_course_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher
@check_edit_course_pyment
def edit_consultant_payment(request,id):
    payment=get_object_or_404(Cosultant_Payment,id=id,status="declined")
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            form=ConsultantPaymentFom(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
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
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:consultant_payment"))
        else:  
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:consultant_payment"))
    context={"form":form}
    return render(request,"edit_consultant_payment.html",context)


@login_required(login_url="accounts:login")
@check_user_is_teacher
def edit_movies_payment(request,slug,id):
    payment=get_object_or_404(Library_Payment,id=id,status="declined")
    movie=get_object_or_404(Movies,slug=slug)
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            if Library_Payment.objects.filter(user=request.user,library_type=3,content_id=movie.id,status="approved").select_related("user").exists():
                messages.success(request,"you already have a payment for this movie")
                return redirect(reverse("accounts:movies_payment"))
            form=MoviesPaymentForm(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/movies-payment/{movie.slug}/{instance.user.username}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/movies-payment/{movie.slug}/{instance.user.username}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:movies_payment"))
        else:  
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:movies_payment"))
    context={"form":form}
    return render(request,"edit_movies_payment.html",context)


@login_required(login_url="accounts:login")
@check_user_is_teacher
def edit_audio_payment(request,slug,id):
    payment=get_object_or_404(Library_Payment,id=id,status="declined")
    track=get_object_or_404(Audio_Tracks,slug=slug)
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            if Library_Payment.objects.filter(user=request.user,library_type=2,content_id=track.id,status="approved").select_related("user").exists():
                messages.success(request,"you already have a payment for this movie")
                return redirect(reverse("accounts:audio_payment"))
            form=MoviesPaymentForm(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/music-payment/{track.slug}/{payment.user.username}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/music-payment/{track.slug}/{payment.user.username}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:audio_payment"))
        else:  
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:audio_payment"))
    context={"form":form}
    return render(request,"edit_audio_payment.html",context)

@login_required(login_url="accounts:login")
@check_user_is_teacher
def edit_audio_book_payment(request,slug,id):
    payment=get_object_or_404(Library_Payment,id=id,status="declined")
    track=get_object_or_404(Audio_Book_Tracks,slug=slug)
    if request.user == payment.user:
        if payment.method == "Western Union" or payment.method == "bank":
            if Library_Payment.objects.filter(user=request.user,library_type=1,content_id=track.id,status="approved").select_related("user").exists():
                messages.success(request,"you already have a payment for this movie")
                return redirect(reverse("accounts:audio_book_payment"))
            form=MoviesPaymentForm(request.POST or None,request.FILES or None,instance=payment)
            form.initial["payment_image"]=None
            if request.method == "POST":
                if form.is_valid():
                    instance=form.save(commit=False)
                    instance.status="pending"
                    image=request.FILES.get("payment_image")
                    if image:
                        url=f"https://storage.bunnycdn.com/{storage_name}/audio-book-payment/{track.slug}/{payment.user.username}/{image}"
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "AccessKey": Storage_Api
                        }
                        response = requests.put(url,data=image,headers=headers)
                        data=response.json()
                        try: 
                            if data["HttpCode"] == 201:
                                instance.payment_image = f"https://{agartha_cdn}/audio-book-payment/{audio_book.track.slug}/{payment.user.username}/{image}"
                                instance.save()
                        except:
                            pass                 
                    instance.save()
                    body="payment edit is waiting for your approve"
                    subject="edit action"
                    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
                    messages.success(request,"Payment Edited Successfully")
                    return redirect(reverse("accounts:audio_book_payment"))
        else:  
            messages.error(request,"You Don't Have Permission")
            return redirect(reverse("accounts:audio_book_payment"))
    context={"form":form}
    return render(request,"edit_audio_book_payment.html",context)

@login_required(login_url="accounts:login")
@check_consultant_refund
def consultant_refund(request,id):   
    payment=get_object_or_404(Cosultant_Payment,id=id)
    refund=Refunds.objects.create(type="consultant_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":payment.get_consultant_date(),"teacher":payment.teacher.user.username}]}
    refund.data=json.dumps(data)
    refund.save()
    messages.success(request,"Your Refund is Being Review By Admin")
    body=f"refund from {request.user.email}"
    subject="refund payment"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    return redirect(reverse("accounts:consultant_payment"))

@login_required(login_url="accounts:login")
@check_course_refund
def course_refund(request,slug,id):   
    payment=get_object_or_404(Payment,id=id)
    refund=Refunds.objects.create(type="course_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","course":payment.course.name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    messages.success(request,"Your Refund is Being Review By Admin")
    body=f"refund from {request.user.email}"
    subject="refund payment"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    return redirect(reverse("accounts:course_payment"))

@login_required(login_url="accounts:login")
@check_movies_refund
def movies_refund(request,slug,id):   
    payment=get_object_or_404(Library_Payment,id=id)
    refund=Refunds.objects.create(type="movie_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","movies":payment.get_movies().name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    messages.success(request,"Your Refund is Being Review By Admin")
    body=f"refund from {request.user.email}"
    subject="refund payment"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    return redirect(reverse("accounts:movies_payment"))
 
 
@login_required(login_url="accounts:login")
@check_music_refund
def music_refund(request,slug,id):   
    payment=get_object_or_404(Library_Payment,id=id)
    refund=Refunds.objects.create(type="music_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","music":payment.get_music().name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    messages.success(request,"Your Refund is Being Review By Admin")
    body=f"refund from {request.user.email}"
    subject="refund payment"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    return redirect(reverse("accounts:audio_payment"))
 


 
@login_required(login_url="accounts:login")
@check_audio_book_refund
def audio_book_refund(request,slug,id):   
    payment=get_object_or_404(Library_Payment,id=id,library_type=1)
    refund=Refunds.objects.create(type="audio_book_payment",content_id=id,user=request.user,transaction_number=payment.transaction_number)
    my_data={"method":payment.method,"amount":payment.amount,"payment_id":payment.id,"data":[{"date":f"{payment.created_at}","Book":payment.get_audio_book().name}]}
    refund.data=json.dumps(my_data)
    refund.save()
    body=f"a new refund from user {request.user.email}"
    subject="new refund"
    send_mail_approve(request,user=request.user.email,subject=subject,body=body)
    messages.success(request,"Your Refund is Being Review By Admin")
    return redirect(reverse("accounts:audio_book_payment"))



