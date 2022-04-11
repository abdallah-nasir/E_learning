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
from datetime import  datetime as dt
from django.core.mail import EmailMessage,get_connection
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from E_learning.all_email import *

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

def home(request):
    teachers=cache.get("teacher_time")
    if teachers:
        teacher_list={}
        for i in teachers:
            if i.user not in teacher_list.keys(): 
                teacher_list[i.user]=i
        teachers=list(teacher_list.values())
    elif teachers == None: 
        teachers=Teacher_Time.objects.filter(available=True).order_by("-id")
        repeat_teacher=cache.set("teacher_time",list(teachers),60*30)
        teachers=cache.get("teacher_time")

        teacher_list={}
        for i in teachers:
            if i.user not in teacher_list.keys(): 
                teacher_list[i.user]=i
        teachers=list(teacher_list.values())
    profiles=cache.get("profiles_teacher")
    if profiles == None:
        profiles=User.objects.filter(account_type="teacher")[:10]
        cache.set("profiles_teacher",profiles,60*60*24)
    context={"teachers":teachers,"profiles":profiles}
    return render(request,"kemet/consultant.html",context)
 
def get_consultant(request,slug):
    try:
        id=request.GET["consultant"]
        teacher_time=get_object_or_404(Teacher_Time,id=id,user__slug=slug,available=True,)
    except:
        return redirect(reverse("consultant:home"))
    context={"teacher":teacher_time}
    return render(request,"kemet/consultant_teacher.html",context)
    
@login_required(login_url="accounts:login")
@validate_post_checkout
def post_payment_data(request,id):
    form=CosultantForm(request.POST or None)
    try:
        if form.is_valid():
            teacher=form.cleaned_data.get("consultant")
            teacher_time=get_object_or_404(Teacher_Time,id=id)
            user,created=UserDataForm.objects.get_or_create(user=request.user,teacher_id=teacher,accomplished=False)
            date=request.POST["date"]
            user.date=dt.strptime(date,'%m/%d/%Y')
            full_name=form.cleaned_data.get("full_name")
            specialization=form.cleaned_data.get("specialization")
            email=form.cleaned_data.get("email")
            phone=form.cleaned_data.get("phone")
            topic=form.cleaned_data.get("topic")
            terms=form.cleaned_data.get("terms")
            method=form.cleaned_data.get("method")
            data={"full_name":full_name,"specialization":specialization,"email":email,
                "phone":phone,"topic":topic,"terms":terms,"method":method,"date":date}
            user.data=json.dumps(data)
            user.save()
            return redirect(reverse("consultant:payment",kwargs={"teacher":teacher_time.id}))
    except:
        return redirect(reverse("consultant:home"))
@login_required(login_url="accounts:login")
@check_user_is_has_consul_checkout
@validate_checkout 
def checkout(request,slug):
    id=request.GET["consultant"]
    date=request.GET["date"]
    teacher=get_object_or_404(Teacher_Time,id=id,user__slug=slug)
    form=CosultantForm(request.POST or None)
    context={"teacher":teacher,"date":date}
    return render(request,"kemet/consultant_checkout.html",context)

@login_required(login_url="accounts:login")
@check_user_is_has_consul
@complete_user_data
@check_user_data_form
def payment(request,teacher):
    teacher=get_object_or_404(Teacher_Time,id=teacher,available=True)
    user_data=get_object_or_404(UserDataForm,user=request.user,teacher=teacher,accomplished=False)
    context={'teacher':teacher,"user_data":user_data}
    return render(request,"kemet/consultant_payment.html",context)


@login_required(login_url="accounts:login")
@check_user_is_has_western
@complete_user_data
@check_user_data_form
def western_payment(request,teacher):
    teacher=get_object_or_404(Teacher_Time,id=teacher,available=True)
    form=PaymentMethodForm(request.POST or None ,request.FILES or None)
    url=f"{request.scheme}://{request.META['HTTP_HOST']}"
    if request.method == 'POST':
        if form.is_valid():
            image=form.cleaned_data.get("image")
            number=form.cleaned_data.get("number")
            user_form=UserDataForm.objects.get(user=request.user,teacher=teacher,accomplished=False)
            user_form.accomplished=True
            user_form.save()
            payment=Cosultant_Payment.objects.create(method="Western Union",amount=teacher.price,user_data=user_form.data,transaction_number=number,
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
            msg = EmailMessage(subject="Payment completed",
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
            return redirect(reverse("accounts:consultant_payment"))
        else:
            messages.error(request,"invalid form")
    context={"form":form,"teacher":teacher,"url":url}
    return render(request,"kemet/consultant_western.html",context)
 

@login_required(login_url="accounts:login")
@check_user_is_has_bank
@complete_user_data
@check_user_data_form
def bank_payment(request,teacher):
    teacher=get_object_or_404(Teacher_Time,id=teacher,available=True)
    form=PaymentMethodForm(request.POST or None ,request.FILES or None)
    url=f"{request.scheme}://{request.META['HTTP_HOST']}"
    if request.method == 'POST':
        if form.is_valid():
            image=form.cleaned_data.get("image")
            number=form.cleaned_data.get("number")
            user_form=UserDataForm.objects.get(user=request.user,teacher=teacher,accomplished=False)
            user_form.accomplished=True
            user_form.save()
            payment=Cosultant_Payment.objects.create(method="bank",amount=teacher.price,user_data=user_form.data,transaction_number=number,
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
            msg = EmailMessage(subject="Payment completed",
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
            return redirect(reverse("accounts:consultant_payment"))
        else:
            messages.error(request,"invalid form")
    context={"form":form,"teacher":teacher,"url":url}
    return render(request,"kemet/consultant_western.html",context)


def random_integer_generator(size = 8, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


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
def paypal_capture(request,teacher_id,order_id,user,user_data_form):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        teacher=get_object_or_404(Teacher_Time,id=teacher_id)
        user=get_object_or_404(User,id=user)
        try:
            if data["status"] == "COMPLETED" :
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                user_form=UserDataForm.objects.get(id=user_data_form)
                user_form.accomplished=True
                user_form.save()
                payment=Cosultant_Payment.objects.create(method="Paypal",amount=teacher.price,transaction_number=transaction,
                    teacher=teacher,user_data=user_form.data,user=user,status="pending")
                messages.add_message(request, messages.SUCCESS,"We Have sent an Email,Please check your Inbox")
                # msg_html = render_to_string("email_order_confirm.html",{"order":order})
                msg = EmailMessage(
                    subject="Payment completed",
                    body="thank you for your payment", 
                    from_email=PAYMENT_EMAIL_USERNAME,
                    to=[user.email],
                    connection=PAYMENT_MAIL_CONNECTION
                    )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                body="new payment is waiting for your approve"
                subject="new payment"
                send_mail_approve(request,user=user.email,subject=subject,body=body)
                return JsonResponse({"status":1})
            else:
                return JsonResponse({"status":0})
        except:
            return JsonResponse({"status":0})


