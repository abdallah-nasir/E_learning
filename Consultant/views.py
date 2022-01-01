from django.shortcuts import render,redirect
from django.urls import reverse
from .models import *
from .forms import *
from .decorators import check_user_is_has_consul
from django.http import JsonResponse
import json,requests,random,string
from django.contrib import messages
from datetime import datetime as dt
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
Storage_Api="b6a987b0-5a2c-4344-9c8099705200-890f-461b"
storage_name="agartha"
library_id="19804"
storage_name="agartha"
agartha_cdn="agartha1.b-cdn.net"
PAYMOB_API_KEY = "ZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6VXhNaUo5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TVRFNE1ESTVMQ0p1WVcxbElqb2lhVzVwZEdsaGJDSjkuU0VhV0IwbjlMVklMeHVKd1NqTFVldDNWc0pqMDVMZjBOVUNuTmZROGZJOFdxREswb3FUOE1pYjBUeTY2MHlXZzRsUGNXU3dhTHZDc0x5RVd1LUtRaVE="  # PAYMOB
PAYMOB_FRAME="269748"
PAYMOB_CONSULT_INT=585334
from django.db.models import F
def home(request):
    category=Category.objects.all()
    form=CosultantForm(request.POST or None,initial={'name':None})
    context={"form":form,"category":category}
    return render(request,"consultant.html",context)

def teacher_ajax(request):
    form=CosultantForm(request.POST or None)
    if request.is_ajax():
        if form.is_valid():
            category=form.cleaned_data.get("name")
            teacher=Teacher_Time.objects.filter(category=category,available=True).values('user__username',"user__id").distinct()
            return JsonResponse(list(teacher),safe=False)
        else:
            print("invalid")
        return JsonResponse({"message":"asd"})
    else:
        return JsonResponse({"message":"not ajax request"})
  

def teacher_ajax_table(request):
    form=CosultantForm(request.POST or None)
    if request.is_ajax():
        print("ajax")
        teacher=request.POST.get("teacher")
        teacher=Teacher_Time.objects.filter(user_id=teacher,available=True)
        list=[]
        host=request.META['HTTP_HOST']
        for i in teacher:
            url=f"/consultant/payment/{i.id}/"
            list.append({"id":i.id,"username":i.user.username.title(),
                "category":i.category.name,"date":i.date,"from":i.from_time.strftime("%I:%M %p"),"to":i.to_time.strftime("%I:%M %p"),
            "url":url,"price":i.price})
        print(list)
    return JsonResponse(list,safe=False)

@login_required(login_url="accounts:login")
@check_user_is_has_consul
def consultant_payment(request,teacher):
    teacher=get_object_or_404(Teacher_Time,id=teacher,available=True)
    form=PaymentForm(request.POST or None ,request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            method=form.cleaned_data["payment_method"]
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]
            consult=Consultant.objects.create(user=request.user
                ,teacher=teacher,status="pending")
            payment=Cosultant_Payment.objects.create(method=method,transaction_number=number,
                consult=consult,user=request.user,status="pending")
            image_url=f"https://storage.bunnycdn.com/{storage_name}/consultant-payment/{payment.user.slug}/{payment.consult.teacher.date}/{image}"
            headers = {
                "AccessKey": Storage_Api,
                "Content-Type": "application/octet-stream",
                }
            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
            print(data)
            try:
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/consultant-payment/{payment.user.slug}/{payment.consult.teacher.date}/{image}"
                    payment.save()
            except:
                pass
            msg = EmailMessage(subject="Payment completed", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[payment.user.email])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            messages.success(request,"We Have sent an Email,Please check your Inbox")
            return redirect(reverse("home:home"))
        else:
            messages.error(request,"invalid form")
    context={"form":form,"teacher":teacher}
    return render(request,"consultant_payment.html",context)


def random_integer_generator(size = 8, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url="accounts:login")
@check_user_is_has_consul
def paymob_payment(request,teacher):
    if request.is_ajax():     
        # return JsonResponse({"frame":PAYMOB_FRAME,"token":123})
        teacher=get_object_or_404(Teacher_Time,id=teacher,available=True)
        merchant_order_id=request.user.id + int(random_integer_generator())
        url_1 = "https://accept.paymob.com/api/auth/tokens"
        data_1 = {"api_key": PAYMOB_API_KEY}
        r_1 = requests.post(url_1, json=data_1)
        token = r_1.json().get("token")
        print(token)
        data_2 = {
            "auth_token": token,
            "delivery_needed": "false",
                "amount_cents":teacher.price * 100,
                "currency": "EGP",
                "merchant_order_id": merchant_order_id,  # 81

                "items": [
        {
            "name": teacher.id,
            "amount_cents": teacher.price * 100,
            "description": f"Teacher {teacher.id}",
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
            "amount_cents": teacher.price * 100,
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
            "integration_id": PAYMOB_CONSULT_INT,
            "lock_order_when_paid": "true"
        }
        url_3 = "https://accept.paymob.com/api/acceptance/payment_keys"
        r_3 = requests.post(url_3, json=data_3)
        payment_token = (r_3.json().get("token"))
        print(payment_token)
        return JsonResponse({"frame":PAYMOB_FRAME,"token":payment_token})



@csrf_exempt    
def check_paymob_payment(request):
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
        teacher_id=data['order']["items"][0]["name"]
        username=data["order"]["shipping_data"]["first_name"]
        user=User.objects.get(username=username)
        teacher=Teacher_Time.objects.get(id=teacher_id)
        consult=Consultant.objects.create(user=user,teacher=teacher,status="pending")
        transaction_number=request.GET["id"]
        Cosultant_Payment.objects.create(method="Paymob",transaction_number=transaction_number,consult=consult,user=user,status="pending")
        messages.success(request,"your request is being review by admin")
    except:
        pass
    return redirect(reverse("accounts:course_payment"))

from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID="AZDbi4r4DSUE9nyMkO0QQjoMwgpfLjpKV7oYbbx_OlumnJM3xtNNoCkHAkevpHfunFJAaqCUSBvnLJez" # paypal
CLIENT_SECRET="ED45Xje6Z5SyKQe3EPTblfvM9gOidJTXq342B602AGNi4stk4i9wduEtYTbPzcGBDhTVAZ0cmbZg5b2w" # paypl

@login_required(login_url="accounts:login")
@check_user_is_has_consul
def paypal_create(request,teacher):
    if request.method =="POST":
        try:
            teacher=get_object_or_404(Teacher_Time,id=teacher)
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
                            "value": teacher.price,
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value":  teacher.price
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
            print("asd")
            data={}
            return JsonResponse(data)
    else:
        return JsonResponse({'details': "invalid request"})         

@login_required(login_url="accounts:login")
def paypal_capture(request,order_id,teacher_id):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        print(data)

        teacher=get_object_or_404(Teacher_Time,id=teacher_id)
        try:
            if data["status"] == "COMPLETED" :
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                consult=Consultant.objects.create(user=request.user
                    ,teacher=teacher,status="pending")
                payment=Cosultant_Payment.objects.create(method="Paypal",transaction_number=transaction,
                   consult=consult,user=request.user,status="pending")
                messages.add_message(request, messages.SUCCESS,"We Have sent an Email,Please check your Inbox")
                # msg_html = render_to_string("email_order_confirm.html",{"order":order})
                msg = EmailMessage(subject="Payment completed", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[consult.user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                return JsonResponse({"status":1})
            else:
                return JsonResponse({"status":0})
        except:
            return JsonResponse({"status":0})
