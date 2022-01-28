from django.db.models.query_utils import Q
from django.shortcuts import render,redirect,reverse
from .models import *
import os
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .forms import *
from .decorators import *
from Frontend.models import *
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse,HttpResponseRedirect
from django.db.models import Q
from itertools import chain
from django.conf import settings
from accounts.models import User
from Consultant.models import Teacher_Time,Consultant,Cosultant_Payment,UserDataForm
from Blogs.models import Blog_Payment,Prices
from django.core.mail import send_mail,EmailMessage,get_connection
from django.contrib.auth.decorators import login_required
from datetime import date
import datetime
from django.forms import ValidationError
from django.core.cache import cache
import requests
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
AccessKey=os.environ["AccessKey"]
Storage_Api=os.environ["Storage_Api"]
library_id=os.environ["library_id"]
storage_name=os.environ['storage_name']
agartha_cdn=os.environ['agartha_cdn']
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]
PAYMOB_FRAME=os.environ["PAYMOB_FRAME"]
PAYMOB_COURSE_INT=os.environ["PAYMOB_COURSE_INT"]
SUPPORT_EMAIL_HOST = os.environ['SUPPORT_EMAIL_HOST']
SUPPORT_EMAIL_USERNAME = os.environ['SUPPORT_EMAIL_USERNAME']
SUPPORT_EMAIL_PASSWORD = os.environ['SUPPORT_EMAIL_PASSWORD']
SUPPORT_EMAIL_PORT = os.environ['SUPPORT_EMAIL_PORT']
SUPPORT_MAIL_CONNECTION = get_connection(
host= SUPPORT_EMAIL_HOST, 
port=SUPPORT_EMAIL_PORT, 
username=SUPPORT_EMAIL_USERNAME, 
password=SUPPORT_EMAIL_PASSWORD, 
use_tls=False
) 
class FailedJsonResponse(JsonResponse):
    def __init__(self, data):
        super().__init__(data)
        self.status_code = 400

def global_search(request):
    qs=request.GET.get("qs")
    courses=Course.objects.filter(Q(name__icontains=qs,status="approved") | Q(details__icontains=qs,status="approved") | Q(branch__name__icontains=qs,status="approved") | Q(branch__category__name__icontains=qs,status="approved") | Q(Instructor__username=qs,status="approved")).distinct() 
    if len(courses) == 0:
        page_obj=[]
        qs=None
    else:
        paginator = Paginator(courses, 8) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    context={"results":courses}
    return render(request,"global_search.html",context)

def course_search(request):
    qs=request.GET.get("qs")
    course=Course.objects.filter(Q(name__icontains=qs,status="approved") | Q(details__icontains=qs,status="approved") | Q(branch__name__icontains=qs,status="approved") | Q(branch__category__name__icontains=qs,status="approved")).distinct() 

    if len(course) == 0:
        page_obj=[]
        qs=None
    else:
        paginator = Paginator(course, 8) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,"course_search.html",{"course":page_obj,"qs":qs})

def home(request):
    data=cache.get("data")
    if data ==None:
        data=get_home_data()
        cache.set("data",data,60*15)
        print("here")
    else:
        data=cache.get("data")
        print("there")
        print(data)
    context={"data":data}
    return render(request,"home.html",context)

def subscribe(request):
    form=SubscribeForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            email=form.cleaned_data.get("email")
            instance.save()
            user=User.objects.filter(email=email)
            if user.exists():
                instance.user=user[0]
                instance.save()
            messages.success(request,"you have subscribed to our daily news")
    return redirect(reverse("home:home"))
def courses(request):
    course=Course.objects.filter(status="approved")
    paginator = Paginator(course, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"course":page_obj}
    return render(request,"courses.html",context)

def branch(request,slug):
    branch=get_object_or_404(Branch,slug=slug)
    course=Course.objects.filter(branch=branch,status="approved")
    paginator = Paginator(course, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"course":page_obj,"branch":branch}
    return render(request,"branch.html",context)

def single_course(request,slug):
    course=get_object_or_404(Course,slug=slug,status="approved")
    form=ReviewForm(request.POST or None)
    if request.method == "POST":
        if request.user.is_authenticated:
            instance=form.save(commit=False)
            if form.is_valid():
                if Reviews.objects.filter(user=request.user,course=course).exists():
                    messages.error(request,"you already submitted to the course")
                    return redirect(reverse("home:course",kwargs={"slug":course.slug}))
                else:
                    instance.user=request.user
                    instance.course=course
                    instance.save()
                    course.reviews.add(instance)
                    course.save()
                    messages.success(request, 'thank you for your opinion')
        else:
            messages.error(request, 'login first')

    context={"course":course,} 
    return render(request,"course-single.html",context)
 
def videos(request,course,slug):
    video=get_object_or_404(Videos,slug=slug)
    if not request.user in video.my_course.students.all():
        messages.error(request,"sorry you should buy course first")
        return redirect(reverse("home:course",kwargs={"slug":video.my_course.slug}))
    else:
        if request.method == "POST":
            if request.user.is_authenticated:
                if Reviews.objects.filter(user=request.user,course=video.my_course).exists():
                    messages.error(request,"you already submitted to the course")
                    return redirect(reverse("home:video",kwargs={"course":course,"slug":video.slug}))
                rate=request.POST.get("rate")
                review=request.POST.get("review")
                print(rate,review)
                if rate and review:
                    if 5 >= int(rate) >= 1:
                        my_review=Reviews.objects.create(user=request.user,review=review,
                            rate=int(rate),course=video.my_course)
                        messages.success(request, 'thank you for your opinion')
                        video.my_course.reviews.add(my_review)
                        video.my_course.save()
                    else:
                        messages.error(request,f'your rate must be between 1 To 5')
                else:
                    messages.error(request,f'invalid Rate / Review')
            else:
                messages.error(request, 'login first')
    context={"video":video,"course":video.my_course}
    return render(request,"video.html",context)

def events(request):
    events=Events.objects.filter(Q(status="approved")|Q(status="start")).distinct()
    paginator = Paginator(events, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"events":page_obj}    
    return render(request,"events.html",context)

def event_single(request,slug):
    event=get_object_or_404(Events,slug=slug)
    if event.status == "approved" or event.status =="start":
        pass
    else:
        messages.error(request,"invalid event date")
        return redirect(reverse("home:events"))
    context={"event":event}
    return render(request,"event_single.html",context)

def teachers(request):
    teahcers=User.objects.filter(account_type="teacher",is_active=True)
    paginator = Paginator(teahcers, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"teachers":page_obj}
    return render(request,"teachers.html",context)

def teacher_single(request,slug):
    teacher=get_object_or_404(User,slug=slug,account_type="teacher",is_active=True)
    courses=Course.objects.filter(Instructor=teacher,status="approved")
    reviews=Teacher_review.objects.filter(teacher=teacher).order_by("-id")
    if request.method == "POST":
        if request.user.is_authenticated:
            if not Teacher_review.objects.filter(user=request.user,teacher=teacher).exists():
                    rate=request.POST.get("rate")
                    review=request.POST.get("review")
                    print(rate,review)
                    if rate and review:
                        if 5 >= int(rate) >= 1:
                            my_review=Teacher_review.objects.create(user=request.user,review=review,
                                        rate=int(rate),teacher=teacher)
                            messages.success(request, 'thank you for your opinion')
                        else:
                            messages.error(request,f'your rate must be between 1 To 5')
                    else:
                        messages.error(request,f'invalid Rate / Review')
 
                            
            else:
                messages.error(request,f'you already submitted your review with Teacher/{teacher.first_name.title()}')
        else:
            messages.error(request, 'login first')

    context={"teacher":teacher,"courses":courses,"reviews":reviews}
    return render(request,"teachers-single.html",context)

def about(request):
    teachers=cache.get("about_teachers")
    print(teachers)
    if teachers == None:
        teachers=User.objects.filter(account_type="teacher",is_active=True).order_by("?")[:8]
        cache.set("about_teachers",teachers,60*15)
    context={"teachers":teachers}
    return render(request,"about.html",context)


   
def category(request,slug):
    blogs=Blog.objects.filter(category__slug=slug)
    categories=Category.objects.all()
    if len(blogs) == 0:
        category_name=[]
        page_obj=None
    else:
        category_name=blogs.first().category.name
        paginator = Paginator(blogs, 8) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj,"categories":categories,"category_name":category_name,"slug":slug,"popular":popular_blogs()}
    return render(request,"category.html",context)

    


def shops(request):
    context={}   
    return render(request,"shops.html",context)

def shop(request):
    context={}
    return render(request,"shop.html",context)


def contact(request):
    form = Support_Form(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            name=form.cleaned_data.get("name")
            email=form.cleaned_data.get("email")
            subject=form.cleaned_data.get("subject")
            message=form.cleaned_data.get("message")
            send_mail( 
            subject,
            message,
            email,
            ["support@agartha.academy"],
            fail_silently=False,
            connection=SUPPORT_MAIL_CONNECTION
        )
            instance.save()
            user= User.objects.filter(email=email.lower())
            if user.exists():
                instance.user = user[0]
                instance.save()
            messages.success(request,"thank you for your message")
    context={}
    return render(request,"contact.html",context)
@login_required(login_url="accounts:login")
def wishlist(request,slug):
    wishlist,created=Wishlist.objects.get_or_create(user=request.user)
    if len(wishlist.course.all()) == 0:
        messages.error(request,"your cart is empty")
        return redirect(reverse("home:home"))
    paginator = Paginator(wishlist.course.all(), 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"course":page_obj} 
    return render(request,"wishlist.html",context)

def wishlist_remove(request):
    if request.user.is_authenticated:
        print("ajax")
        id=request.GET["id"]
        my_course=get_object_or_404(Course,id=id)
        try:
            wishlist,created=Wishlist.objects.get_or_create(user=request.user)
            wishlist.course.remove(my_course)
            my_course.likes -=1
            my_course.save()
            return JsonResponse({"id":my_course.id,"shop":wishlist.course.count(),"count":wishlist.course.count()})

        except: 
            return FailedJsonResponse({"message":"invalid id"})
    else:
        print("here")
        return FailedJsonResponse({"message":"error message"})

# @login_required(login_url="accounts:login")
def wishlist_add(request):
    if request.user.is_authenticated:
        id=request.GET["id"]   
        my_course=get_object_or_404(Course,id=id)
        try:
            wishlist,created=Wishlist.objects.get_or_create(user=request.user)
            print("ajax")
            if not my_course in wishlist.course.all():
                wishlist.course.add(my_course)
                my_course.likes +=1
                my_course.save()
                print("added")
            return JsonResponse({"color":"yellow","id":my_course.id,"shop":wishlist.course.count(),"count":my_course.likes})
            # else:
            #     wishlist.course.remove(my_course)
            #     my_course.likes -=1
            #     my_course.save()
            #     return JsonResponse({"color":"white","id":my_course.id,"shop":wishlist.course.count(),"count":my_course.likes})
        except: 
            return FailedJsonResponse({"message":"invalid id"})
    else:
        print("here")
        return FailedJsonResponse({"message":"error message"})


#######################################
#payment

def random_integer_generator(size = 8, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url="accounts:login")
@check_if_user_in_course
@check_if_user_in_pending_payment
@check_if_user_data_complete
def checkout(request,course):
    form=CashForm(request.POST or None,request.FILES or None)
    my_course=get_object_or_404(Course,slug=course)
    if request.method == "POST":
        methods=["Bank Transaction","Western Union","Vodafone Cash"]
        if form.is_valid():
            try:
                method= request.POST["payment"]
            
                if method in methods:
                    image=request.FILES["payment_image"]
                    number=form.cleaned_data["number"]
                    image_url=f"https://storage.bunnycdn.com/{storage_name}/course-payment/{my_course.slug}/{image}"
                    headers = {
                        "AccessKey": Storage_Api,
                        "Content-Type": "application/octet-stream",
                        }
                    response = requests.put(image_url,data=image,headers=headers)
                    data=response.json()
                    print(data)

                    payment=Payment.objects.create(user=request.user,method=method,transaction_number=number,course=my_course,       
                        status="pending")
                    try:
                        if data["HttpCode"] == 201:
                            payment.payment_image = f"https://{agartha_cdn}/course-payment/{my_course.slug}/{image}"
                            payment.save()
                    except:
                        pass
                    msg = EmailMessage(subject="order confirm", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[request.user.email])
                    msg.content_subtype = "html"  # Main content is now text/html
                    msg.send()
                    messages.success(request,"We Have sent an Email, Please check your Inbox")
                    return redirect(reverse("home:course",kwargs={"slug":my_course.slug}))
                else:
                    return redirect(reverse("home:home"))
            except:
                return redirect(reverse("home:home"))

    context={"form":form,"course":my_course,"frame": PAYMOB_FRAME, "payment_token": 11}
    return render(request,"checkout.html",context)        
 
def payment_method_ajax(request):
    course_id=request.POST.get("ajax_course")
    print(course_id)
    course=get_object_or_404(Course,id=course_id)
    payment_form=PaymentMethodForm(request.POST or None,request.FILES or None)
    my_method=None
    if request.is_ajax():     
        my_method=request.POST.get("payment_method")
        print(my_method)
        if payment_form.is_valid():
            return JsonResponse({"payment":my_method})
        else:
            return FailedJsonResponse({"payment":payment_form.errors})



from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID=os.environ["CLIENT_ID"]
CLIENT_SECRET=os.environ["CLIENT_SECRET"]
@login_required(login_url="accounts:login")
@check_if_user_in_course
@check_if_user_in_pending_payment
@check_if_user_data_complete
def create(request,course):
    if request.method =="POST":
        try:
            course=get_object_or_404(Course,slug=course)
           
            environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
            client = PayPalHttpClient(environment)
            create_order = OrdersCreateRequest()
            #order            
            create_order.request_body (

            {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value":course.get_price(),
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value":  course.get_price()
                                }
                                },
                            },                                  


                    }
                ],      
                

            }     
        ) 
        
            response = client.execute(create_order)
            data = response.result.__dict__['_dict']      

            # print(data)
            return JsonResponse(data)
        except:
            print("except")
            data={}
            return JsonResponse(data)
    else:
        print("not here")
        return JsonResponse({'details': "invalid request"})         

@login_required(login_url="accounts:login")
def capture(request,order_id,course):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        print(data)
        payment=Payment.objects.create(user=request.user,course_id=course,status="pending")
        try:
            if data["status"] == "COMPLETED" and payment.status == "pending":
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                payment.transaction_number=transaction
                payment.method ="Paypal"
                payment.save()
                # payment.course.students.add(request.user)     i pussed adding student automaticly
                # payment.course.save()
                messages.add_message(request, messages.SUCCESS,"We Have sent an Email,Please check your Inbox")
                # msg_html = render_to_string("email_order_confirm.html",{"order":order})
                msg = EmailMessage(subject="order confirm", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[payment.user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                return JsonResponse({"status":1})
            else:
                return JsonResponse({"status":0})
        except:
            return JsonResponse({"status":0})

# #paymob


@login_required(login_url="accounts:login")
@check_if_user_in_course
@check_if_user_in_pending_payment
@check_if_user_data_complete
def paymob_payment(request,course):
    if request.is_ajax():     
        
        # return JsonResponse({"frame":PAYMOB_FRAME,"token":123})

        my_course=get_object_or_404(Course,slug=course)
        merchant_order_id=request.user.id + int(random_integer_generator())
        url_1 = "https://accept.paymob.com/api/auth/tokens"
        data_1 = {"api_key": PAYMOB_API_KEY}
        r_1 = requests.post(url_1, json=data_1)
        token = r_1.json().get("token")
        print(token)
        data_2 = {
            "auth_token": token,
            "delivery_needed": "false",
                "amount_cents":my_course.get_price() * 100,
                "currency": "EGP",
                "merchant_order_id": merchant_order_id,  # 81

                "items": [
        {
            "name": my_course.slug,
            "amount_cents": my_course.get_price() * 100,
            "description": "course",
            "quantity": "1"
        },
    
        ],
                "shipping_data": {
                    "apartment": "803",
                    "email": request.user.email,
                    "floor": "42",
                    "first_name": request.user.username,
                    "street": "Ethan Land",
                    "building": "8028",
                    "phone_number": request.user.phone,
                    "postal_code": "01898",
                    "extra_description": "8 Ram , 128 Giga",
                    "city": "Jaskolskiburgh",
                    "country": "CR",
                    "last_name": request.user.last_name,
                    "state": "Utah"
                },
                "shipping_details": {
                    "notes": " test",
                    "number_of_packages": 1,
                    "weight": 1,
                    "weight_unit": "Kilogram",
                    "length": 1,
                    "width": 1,
                    "height": 1,
                    "contents": "product of some sorts"
                }
            }
        url_2 = "https://accept.paymob.com/api/ecommerce/orders"
        r_2 = requests.post(url_2, json=data_2)
        my_id = r_2.json().get("id")
        if my_id == None:
            print("none")
            r_2 = requests.get(url_2, json=data_2)
            my_id = r_2.json().get("results")[0]["id"]

        data_3 = {
            "auth_token": token,
            "amount_cents": my_course.get_price() * 100,
            "expiration": 15*60,
            "order_id": my_id,
            "billing_data": {
                "apartment": "803",
                "email": request.user.email,
                "floor": "42",
                "first_name": request.user.username,
                "street": "Ethan Land",
                "building": "8028",
                "phone_number": request.user.phone,
                "shipping_method": "PKG",
                "postal_code": "01898",
                "city": "Jaskolskiburgh",
                "country": "CR",
                "last_name": request.user.last_name,
                "state": "Utah"
            },
            "currency": "EGP",
            "integration_id": PAYMOB_COURSE_INT,
            "lock_order_when_paid": "true"
        }
        url_3 = "https://accept.paymob.com/api/acceptance/payment_keys"
        r_3 = requests.post(url_3, json=data_3)
        payment_token = (r_3.json().get("token"))
        print(payment_token)
        return JsonResponse({"frame":PAYMOB_FRAME,"token":payment_token})



@csrf_exempt    
def check_paymob_course_payment(request):
    try:
        id=request.GET["id"]
        url_1 = "https://accept.paymob.com/api/auth/tokens"
        data_1 = {"api_key": PAYMOB_API_KEY}
        r_1 = requests.post(url_1, json=data_1)
        token = r_1.json().get("token")
        url_2=f"https://accept.paymob.com/api/acceptance/transactions/{id}"
        header= {"Bearer":token}
        r_2= requests.get(url_2,  headers={'Authorization': f'{token}'})    
        data=r_2.json() 
        print(data) 
        descrption=data["order"]["items"][0]["description"]
        username=data["order"]["shipping_data"]["first_name"]
        transaction_number=request.GET["id"]
        name=data['order']["items"][0]["name"]
        user=User.objects.get(username=username)
        if descrption == "course":
            print("course")
            course=Course.objects.get(slug=name)
            Payment.objects.create(method="Paymob",transaction_number=transaction_number,course=course,user=user,status="pending")
            next=("accounts:course_payment")
            messages.success(request,"your request is being review by admin")
        elif descrption =="consultant": 
            teacher=Teacher_Time.objects.get(id=name)
            transaction_number=request.GET["id"]
            user_form=UserDataForm.objects.get(user=user,teacher=teacher,accomplished=False)
            user_form.accomplished=True
            user_form.save()
            Cosultant_Payment.objects.create(method="Paymob",user_data=user_form.data,transaction_number=transaction_number,teacher=teacher,user=user,status="pending")
            next=("accounts:consultant_payment")
            messages.success(request,"your request is being review by admin")
        elif descrption == "blogs":
            prices=Prices.objects.get(id=name)
            now= date.today()
            payment=Blog_Payment.objects.create(method="Paymob",transaction_number=transaction_number,user=user,created_at=now)
            if prices.get_duration() == 'monthly':
                payment.expired_at= now + datetime.timedelta(days=30*6)
            else:
                payment.expired_at= now + datetime.timedelta(days=365)
            payment.save()
            next=("accounts:blog_payment")
            messages.success(request,"your request is being review by admin")
    except:
        next=("home:home")
        pass
    return redirect(reverse(next))
#######################################
#payment

def success(request):   
    return render(request,"success.html")
        
def failed(request):   
    return render(request,"failed.html")
##########################

def faqs(request):
    return render(request,"faqs.html")

def terms(request):
    terms=Terms.objects.last()
    return render(request,"terms.html",{"terms":terms})
def privacy(request):
    privacy=Privacy.objects.last()
    return render(request,"privacy.html",{"privacy":privacy})

################  errors

def my_custom_page_not_found_view(request, exception, template_name="404.html"):
    response = render(request,template_name,context={"error":404})
    response.status_code = 404
    return response
  

def my_custom_error_view(request, template_name="404.html"):
    response = render(request,template_name,context={"error":500})
    response.status_code = 500
    return response
def my_custom_permission_denied_view(request, exception, template_name="404.html"):
    response = render(request,template_name,context={"error":403})
    response.status_code = 403
    return response

def my_custom_bad_request_view(request, exception, template_name="404.html"):
    response = render(request,template_name,context={"error":400})
    response.status_code = 400
    return response