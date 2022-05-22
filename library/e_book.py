from django.shortcuts import render
from .models import *
from Blogs.models import Blog
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
from E_learning.all_email import *
Storage_Api=os.environ["Storage_Api"]
storage_name=os.environ["storage_name"]
library_id=os.environ["library_id"]
storage_name=os.environ["storage_name"]
agartha_cdn=os.environ['agartha_cdn']

from paypalcheckoutsdk.orders import OrdersCreateRequest 
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID=os.environ["CLIENT_ID"] # paypal
CLIENT_SECRET=os.environ["CLIENT_SECRET"] # paypl


def get_home_cache_data():
    audios=Audio_Tracks.objects.filter(status="approved").select_related("user").order_by("-id")[:13]
    artists=Artist.objects.filter(status="approved").select_related("user")[:8]
    last_songs=Music.objects.all().select_related("track").order_by("-id")[:6]
    context={"audios":audios,"artists":artists,"music":last_songs}
    return context



@login_required(login_url="accounts:login")
def books(request):
    tracks=E_Book.objects.filter(status="approved").select_related("user")
    paginator = Paginator(tracks, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"tracks":page_obj}
    return render(request,"library/e-book/books.html",context)

@login_required(login_url="accounts:login")
def single_book(request,slug):
    track=get_object_or_404(E_Book,slug=slug,status="approved")
    if track.price > 0:
        if track.buyers.filter(id=request.user.id).exists():
            status = False
        else:
            status = True
    else:
        status = False
    context={"book":track,"status":status}
    return render(request,"library/e-book/single_book.html",context)
 
@login_required(login_url="accounts:login")
def comment(request,slug):
    track=get_object_or_404(E_Book,slug=slug,status="approved")
    form=CommentsForm(request.POST)
    if Comments.objects.filter(user=request.user,library=4,content_id=track.id).select_related("user").exists():
        messages.error(request,"you already have a comment for this Book")
    else: 
        if form.is_valid():
            comment=form.cleaned_data.get("comment")
            comment=Comments.objects.create(user=request.user,library=4,content_id=track.id,comment=comment)
            track.comments.add(comment)
            track.save()
            messages.success(request,"thank you for your review")
    return redirect(reverse('library:e_book:single_book',kwargs={"slug":slug}))


@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_e_book_payment_page
def book_payment(request,slug):
    track=get_object_or_404(E_Book,slug=slug,status="approved")
    if int(track.get_price()) <= 0:
        return redirect(reverse("library:e_book:single_book",kwargs={"slug":slug}))
    context={"book":track}
    return render(request,"library/e-book/payment.html",context)
 
@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_e_book_payment_western
def western_payment(request,slug):
    form=PaymentForm(request.POST or None ,request.FILES or None)
    track=get_object_or_404(E_Book,slug=slug,status="approved")
    if request.method == 'POST':
        if form.is_valid():
            now= datetime.date.today()
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]
            payment=Library_Payment.objects.create(user=request.user,
            method="Western Union",content_id=track.id,library_type=4,amount=track.get_price(), transaction_number=number,status="pending",created_at=now)
            image_url=f"https://storage.bunnycdn.com/{storage_name}/e-book-payment/{track.slug}/{payment.user.username}/{image}"
            headers = {
                "AccessKey": Storage_Api, 
                "Content-Type": "application/octet-stream",
                }
            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/e-book-payment/{track.slug}/{payment.user.username}/{image}"
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
            return redirect(reverse("accounts:e_book_payment"))
        else:
            messages.error(request,"invalid form")
            return redirect(reverse("library:e_book:e_book_payment",kwargs={"slug":track.slug}))



@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_e_book_payment_bank
def bank_payment(request,slug):
    form=PaymentForm(request.POST or None ,request.FILES or None)
    track=get_object_or_404(E_Book,slug=slug,status="approved")
    if request.method == 'POST':
        if form.is_valid():
            now= datetime.date.today()
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]
            payment=Library_Payment.objects.create(user=request.user,
            method="Western Union",content_id=track.id,library_type=4,amount=track.get_price(), transaction_number=number,status="pending",created_at=now)
            image_url=f"https://storage.bunnycdn.com/{storage_name}/e-book-payment/{track.slug}/{payment.user.username}/{image}"
            headers = {
                "AccessKey": Storage_Api, 
                "Content-Type": "application/octet-stream",
                }
            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
            try:
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/e-book-payment/{track.slug}/{payment.user.username}/{image}"
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
            return redirect(reverse("accounts:e_payment"))
        else:
            messages.error(request,"invalid form")
            return redirect(reverse("library:e_book:e_payment",kwargs={"slug":track.slug}))




@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@complete_user_data
def paypal_create(request,id):
    if request.method =="POST":
        try:
            track=get_object_or_404(E_Book,id=id,status="approved")
            environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
            client = PayPalHttpClient(environment)
            create_order = OrdersCreateRequest()
            #order            
            create_order.request_body(
            {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": int(track.get_price()),
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value":  int(track.get_price())
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
def paypal_capture(request,order_id,track_id):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        track=get_object_or_404(E_Book,id=track_id)
        try:
            if data["status"] == "COMPLETED":
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                now= datetime.date.today()
                payment=Library_Payment.objects.create(method="Paypal",
                transaction_number=transaction,content_id=track.id,amount=track.get_price(),status="pending",user=request.user,created_at=now,library_type=4)
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


@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_e_book_user
def read_book(request,slug):
    book=get_object_or_404(E_Book,status="approved")

    context={"book":book}
    return render(request,"library/e-book/read_book.html",context)

 