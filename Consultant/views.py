from django.shortcuts import render,redirect
from django.urls import reverse
from .models import *
from home.forms import PaymentMethodForm
from .forms import *

import os
from .decorators import *
from django.http import JsonResponse
import json,requests,random,string
from django.contrib import messages
from datetime import datetime as dt
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
Storage_Api=os.environ["Storage_Api"]
storage_name=os.environ["storage_name"]
library_id=os.environ["library_id"]
storage_name=os.environ["storage_name"]
agartha_cdn=os.environ['agartha_cdn']
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]
PAYMOB_FRAME=os.environ["PAYMOB_FRAME"]
PAYMOB_CONSULT_INT=os.environ['PAYMOB_CONSULT_INT']
from django.db.models import F
from datetime import date

def teacher_table(request):
    category=request.GET.get("name")
    print(category)
    teacher=Teacher_Time.objects.filter(category=category,available=True).order_by("start_time")
    teacher_list=[]
    if teacher:
        for i in teacher:
            teacher_list.append({"title":f"{i.user.first_name.title()}","start":f"{i.start_time}","end":f"{i.end_time}","url":f"{i.get_teacher_url_consultant()}"})
        teachers=json.dumps(teacher_list)
        data={"last":teacher.first().start_time,"teachers":teachers,"count":teacher.count()}
    else:
        data = {"teachers":None}
    return data

def home(request):
    category=Category.objects.all()
    try:
        name=request.GET["name"]
        result=teacher_table(request)
        if result["teachers"] == None:
            time= date.today()
            form=None
            count=0
            teachers=[]
        else:
            form=CosultantForm(request.GET or None)
            time=result["last"]
            teachers=result["teachers"]
            count=result["count"]
        context={"form":form,"category":category,"date":time,"teachers":teachers,"count":count,"name":1}
    except:
        form=CosultantForm(request.GET or None)
        context={"name":None,"form":form,"count":0}
    return render(request,"consultant.html",context)

@check_teacher_dates
def get_consultant(request,slug):
    # user=get_object_or_404(User,slug=slug)
    time=request.GET.get("time")
    teacher_time=get_object_or_404(Teacher_Time,user__slug=slug,id=time,available=True)
    context={"teacher":teacher_time}
    return render(request,"consultant_teacher.html",context)
@login_required(login_url="accounts:login")
@check_user_is_has_consul
# @check_teacher_dates_teacher
@complete_user_data
def consultant_payment(request,teacher):
    teacher=get_object_or_404(Teacher_Time,id=teacher,available=True)
    form=PaymentMethodForm(request.POST or None ,request.FILES or None)
    url=f"{request.scheme}://{request.META['HTTP_HOST']}"
    if request.method == 'POST':
        if form.is_valid():
            image=form.cleaned_data.get("image")
            number=form.cleaned_data.get("number")
            payment=Cosultant_Payment.objects.create(method="Western Union",transaction_number=number,
                teacher=teacher,user=request.user,status="pending")
            image_url=f"https://storage.bunnycdn.com/{storage_name}/consultant-payment/{payment.user.slug}/{payment.teacher.id}/{image}"
            headers = {
                "AccessKey": Storage_Api,
                "Content-Type": "application/octet-stream",
                }
            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
            print(data)
            try:
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/consultant-payment/{payment.user.slug}/{payment.teacher.id}/{image}"
                    payment.save()
            except:
                pass
            msg = EmailMessage(subject="Payment completed", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[payment.user.email])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            messages.success(request,"We Have sent an Email,Please check your Inbox")
            return redirect(reverse("accounts:consultant_payment"))
        else:
            messages.error(request,"invalid form")
    context={"form":form,"teacher":teacher,"url":url}
    return render(request,"consultant_payment.html",context)


def random_integer_generator(size = 8, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url="accounts:login")
@check_user_is_has_consul
@complete_user_data
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
            "description":"consultant",
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




from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID=os.environ['CLIENT_ID']
CLIENT_SECRET=os.environ["CLIENT_SECRET"]

@login_required(login_url="accounts:login")
@check_user_is_has_consul
@complete_user_data
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

# @login_required(login_url="accounts:login")
def paypal_capture(request,teacher_id,order_id,user):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        print(data)

        teacher=get_object_or_404(Teacher_Time,id=teacher_id)
        user=get_object_or_404(User,id=user)
        try:
            if data["status"] == "COMPLETED" :
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                payment=Cosultant_Payment.objects.create(method="Paypal",transaction_number=transaction,
                    teacher=teacher,user=user,status="pending")
                messages.add_message(request, messages.SUCCESS,"We Have sent an Email,Please check your Inbox")
                # msg_html = render_to_string("email_order_confirm.html",{"order":order})
                msg = EmailMessage(subject="Payment completed", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                return JsonResponse({"status":1})
            else:
                return JsonResponse({"status":0})
        except:
            return JsonResponse({"status":0})


def test(request):
    teachers=Teacher_Time.objects.all()  #title url start end
    data=[{"title":"event 1","start":"2020-02-07","end":"2020-02-08"},{"title":"event 1","start":"2020-02-07","end":"2020-02-08"},{"title":"event 1","start":"2020-02-07","end":"2020-02-08"},{"title":"event 1","start":"2020-02-07","end":"2020-02-08"}]
    context={"data":json.dumps(data)}
    return render(request,"consultant_test.html",context)