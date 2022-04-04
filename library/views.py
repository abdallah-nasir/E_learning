from django.shortcuts import render
from .models import *
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail,EmailMessage,get_connection
from django.http import JsonResponse
from .decorators import *
from .forms import PaymentForm,CommentsForm
import os,requests
Storage_Api=os.environ["Storage_Api"]
storage_name=os.environ["storage_name"]
library_id=os.environ["library_id"]
storage_name=os.environ["storage_name"]
agartha_cdn=os.environ['agartha_cdn']
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]  # PAYMOB
PAYMOB_FRAME=os.environ["PAYMOB_FRAME"]
PAYMOB_BLOG_INT=os.environ['PAYMOB_BLOG_INT']
from E_learning.all_email import *

def get_library_home_data():
    audio_libraries=Library.objects.filter(type=3).order_by("-id")[:8]
    e_book_libraries=Library.objects.filter(type=4).order_by("-id")[:8]
    context={"audios":audio_libraries,"e_books":e_book_libraries}
    return contrext
@login_required(login_url="accounts:login")
def home(request):
    # data=get_library_home_data()
    # paginator = Paginator(libraries, 9) 
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    # context={"data":data}
    return render(request,"library/home.html")
   

@login_required(login_url="accounts:login")
def movies(request):
    movies=Movies.objects.filter(status="approved")
    paginator = Paginator(movies, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"movies":page_obj}
    return render(request,"library/movies.html",context)


@login_required(login_url="accounts:login")
def single_movie(request,slug):
    movie=get_object_or_404(Movies,slug=slug,status="approved")
    context={"movie":movie}
    return render(request,"library/single_movie.html",context)

@login_required(login_url="accounts:login")
@check_if_in_can_watch_movie
def show_movie(request,slug):
    movie=get_object_or_404(Movies,slug=slug,status="approved")
    context={"movie":movie}
    return render(request,"library/show_movie.html",context)

@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@movies_check_payment
def movie_payment(request,slug):
    movie=get_object_or_404(Movies,slug=slug,status="approved")
    if int(movie.get_price()) <= 0:
        return redirect(reverse("library:single_movie",kwargs={"slug":slug}))
    context={"movie":movie}
    return render(request,"library/payment.html",context)

@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_if_there_payment
def create_movie_western_payment(request,slug):
    form=PaymentForm(request.POST or None ,request.FILES or None)
    movie=get_object_or_404(Movies,slug=slug,status="approved")
    if request.method == 'POST':
        if form.is_valid():
            now= datetime.date.today()
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]
            payment=Library_Payment.objects.create(user=request.user,
            method="Western Union",content_id=movie.id,library_type=3,amount=movie.get_price(), transaction_number=number,status="pending",created_at=now)
            image_url=f"https://storage.bunnycdn.com/{storage_name}/movies-payment/{movie.slug}/{payment.user.username}/{image}"
            headers = {
                "AccessKey": Storage_Api, 
                "Content-Type": "application/octet-stream",
                }
            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
            print(data) 
            try:
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/movies-payment/{movie.slug}/{payment.user.username}/{image}"
                    payment.save()
            except:
                pass
            msg = EmailMessage(
                subject="Payment completed", 
                body="thank you for your payment",
                from_email=PAYMENT_EMAIL_USERNAME,
                to=[payment.user.email],
                connection=PAYMENT_MAIL_CONNECTION
                )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            body="new payment is waiting for your approve"
            subject="new payment"
            send_mail_approve(request,user=payment.user.email,subject=subject,body=body)
            messages.success(request,"We Have sent an Email,Please check your Inbox")
            return redirect(reverse("accounts:movies_payment"))
        else:
            messages.error(request,"invalid form")
            print(form.errors)
            return redirect(reverse("library:movie_payment",kwargs={"slug":movie.slug}))

from paypalcheckoutsdk.orders import OrdersCreateRequest 
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID=os.environ["CLIENT_ID"] # paypal
CLIENT_SECRET=os.environ["CLIENT_SECRET"] # paypl

@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@complete_user_data
def paypal_create(request,id):
    if request.method =="POST":
        try:
            movie=get_object_or_404(Movies,id=id,status="approved")
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
                            "value": movie.price,
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value":  movie.price
                                }
                                },
                            },                                  
                    }
                ],      
            }     
        ) 
    
            response = client.execute(create_order)
            data = response.result.__dict__['_dict']      
            return JsonResponse(data)
        except:
            data={}
            return JsonResponse(data)
    else:
        return JsonResponse({'details': "invalid request"})         

@login_required(login_url="accounts:login")
def paypal_capture(request,order_id,movie_id):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        movie=get_object_or_404(Movies,id=movie_id)
        try:
            if data["status"] == "COMPLETED":
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                now= datetime.date.today()
                payment=Library_Payment.objects.create(method="Paypal",
                transaction_number=transaction,content_id=movie.id,amount=movie.get_price(),status="pending",user=request.user,created_at=now,library_type=3)
                messages.add_message(request, messages.SUCCESS,"We Have sent an Email,Please check your Inbox")
                # msg_html = render_to_string("email_order_confirm.html",{"order":order})
                msg = EmailMessage(
                    subject="Payment completed", 
                    body="thank you for your payment",
                    from_email=PAYMENT_EMAIL_USERNAME, 
                    to=[payment.user.email],
                    connection=PAYMENT_MAIL_CONNECTION
                    )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                body="new payment is waiting for your approve"
                subject="new payment"
                send_mail_approve(request,user=payment.user.email,subject=subject,body=body)
                return JsonResponse({"status":1})
            else:
                return JsonResponse({"status":0})
        except:
            return JsonResponse({"status":0})

def random_integer_generator(size = 8, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@complete_user_data
def paymob_payment(request,id):
    if request.is_ajax():     
        # return JsonResponse({"frame":PAYMOB_FRAME,"token":123})
        movie=Movies.objects.get(id=id)
        merchant_order_id=request.user.id + int(random_integer_generator())
        url_1 = "https://accept.paymob.com/api/auth/tokens"
        data_1 = {"api_key": PAYMOB_API_KEY}
        r_1 = requests.post(url_1, json=data_1)
        token = r_1.json().get("token")
        data_2 = {
        "auth_token": token,
        "delivery_needed": "false",
            "amount_cents":movie.get_price() * 100,
            "currency": "EGP",
            "merchant_order_id": merchant_order_id,  # 81

            "items": [
    {
        "name": movie.id,
        "amount_cents": movie.get_price() * 100,
        "description": "movies",  
        "quantity": "1"
    },
    {
        "name": movie.id,
        "amount_cents": movie.get_price() * 100,
        "description": 3,        #library_type  
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
                "phone_number": f"{request.user.phone}",   
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
            r_2 = requests.get(url_2, json=data_2)
            my_id = r_2.json().get("results")[0]["id"]

        data_3 = {
            "auth_token": token,
            "amount_cents": movie.get_price() * 100,
            "expiration": 15*60,
            "order_id": my_id,
            "billing_data": {
                "apartment": "803",
                "email": request.user.email,
                "floor": "42",
                "first_name": request.user.username,
                "street": "Ethan Land",
                "building": "8028", 
                "phone_number":f"{request.user.phone}",
                "shipping_method": "PKG",
                "postal_code": "01898",
                "city": "Jaskolskiburgh",
                "country": "CR",
                "last_name": request.user.last_name,
                "state": "Utah"
            },
            "currency": "EGP",
            "integration_id": PAYMOB_BLOG_INT,
            "lock_order_when_paid": "true"
        }
        url_3 = "https://accept.paymob.com/api/acceptance/payment_keys"
        r_3 = requests.post(url_3, json=data_3)
        payment_token = (r_3.json().get("token"))
        if payment_token == None:
            success=0
        else:
            success=1
        print(data_2["items"])
        return JsonResponse({"success":success,"frame":PAYMOB_FRAME,"token":payment_token})


@login_required(login_url="accounts:login")
def create_movies_comment(request,slug):
    movie=get_object_or_404(Movies,slug=slug,status="approved")
    form=CommentsForm(request.POST)
    if Comments.objects.filter(user=request.user,library=3,content_id=movie.id).select_related("user").exists():
        messages.error(request,"you already have a comment for this movie")
    else:
        if form.is_valid():
            comment=form.cleaned_data.get("comment")
            comment=Comments.objects.create(user=request.user,library=3,content_id=movie.id,comment=comment)
            movie.comments.add(comment)
            movie.save()
            messages.success(request,"thank you for your review")
    return redirect(reverse('library:single_movie',kwargs={"slug":slug}))

