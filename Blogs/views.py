from django.shortcuts import render
import os
# Create your views here.
from django.db.models.query_utils import Q
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import *
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .forms import *
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse,HttpResponseRedirect
from django.db.models import Q
from itertools import chain
from django.conf import settings
from accounts.models import User
from django.core.mail import send_mail,EmailMessage,get_connection
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from datetime import datetime
from django.forms import ValidationError
from .decorators import *
import requests,string
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]  # PAYMOB
PAYMOB_FRAME=os.environ["PAYMOB_FRAME"]
PAYMOB_BLOG_INT=os.environ['PAYMOB_BLOG_INT']
from E_learning.all_email import *

Storage_Api=os.environ["Storage_Api"]
storage_name=os.environ["storage_name"]
agartha_cdn=os.environ['agartha_cdn']

@login_required(login_url="accounts:login")
def home(request):
    blog_data=cache.get("blog_data")
    if blog_data == None:
        data=get_blog_data()
        cache.set("blog_data",data,60*60*24)
    else:
        data=cache.get("blog_data")     
    blogs=data["blogs"]
    paginator = Paginator(blogs, 9) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj,"data":data}
    try:
        index=request.GET["index"]
        return render(request,"blogs_2.html",context)
    except:
        return render(request,"blogs.html",context)
    
@login_required(login_url="accounts:login")
def category(request,slug):
    category=get_object_or_404(Category,slug=slug)
    blogs=Blog.objects.filter(category=category,domain_type=1,status="approved").select_related("category").order_by("-id")
    blog_data=cache.get("blog_data")
    if blog_data == None:
        data=get_blog_data()
        cache.set("blog_data",data,60*15)
    else:
        data=cache.get("blog_data")
    paginator = Paginator(blogs, 9) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"blogs_category.html",{'blogs':blogs,"data":data})


@login_required(login_url="accounts:login")
@check_user_is_member
@check_blogs_payment_status
def single_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    comment_form=CommentForm(request.POST or None)
    viewers=blog.check_blog_viwers(request.user)
    categories=recent_categories()
    context={"blog":blog,"categories":categories,"comment_form":comment_form}
    return render(request,"blog.html",context)

@login_required(login_url="accounts:login")
def blog_search(request):
    qs=request.GET.get("search")
    blog=Blog.objects.filter(Q(name__icontains=qs,status="approved") | Q(details__icontains=qs,status="approved") | Q(category__name__icontains=qs,status="approved") |Q(tags__name__icontains=qs,status="approved")).exclude(domain_type=2).distinct() 
    if len(blog) == 0:
        qs=None
        page_obj=[]
    else:
        paginator = Paginator(blog, 9) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,"blog_search.html",{"blogs":page_obj,"qs":qs})
@login_required(login_url="accounts:login")
@complete_user_data
def blog_comment(request,id):
    if request.user.is_authenticated:
        form=CommentForm(request.POST)
        blog=get_object_or_404(Blog,id=id)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.user=request.user
            instance.blog=blog
            instance.save()
            instance.blog.comments.add(instance)
            instance.blog.save()
            form=CommentForm()
            messages.success(request,"Thank You For Your Comment")
    else:
        messages.error(request,"You Should Sign in First")
    return redirect(reverse("blogs:blog",kwargs={"slug":instance.blog.slug}))

@login_required(login_url="accounts:login")
@complete_user_data
def blog_comment_reply(request,id,reply):
    if request.user.is_authenticated:
        form=ReplyForm(request.POST)
        blog=get_object_or_404(Blog,id=id)
        try:
            comment=blog.comments.get(id=reply)
        except:
            return redirect(reverse("blogs:blog",kwargs={"slug":blog.slug}))
        if form.is_valid():
            instance=form.save(commit=False)
            instance.user=request.user
            instance.blog=blog
            instance.comment=comment
            instance.save()
            form=CommentForm()
            messages.success(request,"Thank You For Your Comment")

    else: 
        messages.error(request,"You Should Sign in First")
    return redirect(reverse("blogs:blog",kwargs={"slug":instance.blog.slug}))
import datetime
@login_required(login_url="accounts:login")
def pricing(request):
    prices=Prices.objects.filter(type=1)
    return render(request,"pricing.html",{'prices':prices})

@login_required(login_url="accounts:login")
@complete_user_data
@check_blogs_payment_western_status
def western_payment(request,id):
    price=get_object_or_404(Prices,id=id)
    form=PaymentForm(request.POST or None,request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            now= datetime.date.today()
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]               
            payment=Blog_Payment.objects.create(user=request.user,
            method="Western Union",amount=price.price,type=1,transaction_number=number,status="pending",created_at=now)
            if price.get_duration() == '3 month':
                payment.expired_at= now + datetime.timedelta(days=30*3)
                price_data={"duration":3,"type":"agartha"}
                payment.data= now + datetime.timedelta(days=30*3)
            if price.get_duration() == '6 month':
                price_data={"duration":6,"type":"agartha"}
                payment.expired_at= now + datetime.timedelta(days=30*6)
            if price.get_duration() == '12 month':
                price_data={"duration":12,"type":"agartha"}
                payment.expired_at= now + datetime.timedelta(days=365)
            url=f"https://storage.bunnycdn.com/{storage_name}/blogs-payment/{request.user.username}/{image}"
            headers = {
                    "Content-Type": "application/octet-stream",
                    "AccessKey": Storage_Api
                }
            response = requests.put(url,data=image,headers=headers)
            data=response.json()
            try: 
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/blogs-payment/{request.user.username}/{image}"
                    payment.save()
            except:
                pass  
            payment.data=json.dumps(price_data)
            payment.save()
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
            return redirect(reverse("accounts:blog_payment"))
        else:
            messages.error(request,"invalid form")
    return redirect(reverse("blogs:payment",kwargs={"id":price.id}))



@login_required(login_url="accounts:login")
@complete_user_data
@check_blogs_payment_bank_status
def bank_payment(request,id):
    price=get_object_or_404(Prices,id=id)
    form=PaymentForm(request.POST or None,request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            now= datetime.date.today()
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]               
            payment=Blog_Payment.objects.create(user=request.user,
            method="bank",amount=price.price,type=1,transaction_number=number,status="pending",created_at=now)
            if price.get_duration() == '3 month': 
                payment.expired_at= now + datetime.timedelta(days=30*3)
                price_data={"duration":3,"type":"agartha"}
                payment.data= now + datetime.timedelta(days=30*3)
            if price.get_duration() == '6 month':
                price_data={"duration":6,"type":"agartha"}
                payment.expired_at= now + datetime.timedelta(days=30*6)
            if price.get_duration() == '12 month':
                price_data={"duration":12,"type":"agartha"}
                payment.expired_at= now + datetime.timedelta(days=365)
            url=f"https://storage.bunnycdn.com/{storage_name}/blogs-payment/{request.user.username}/{image}"
            headers = {
                    "Content-Type": "application/octet-stream",
                    "AccessKey": Storage_Api
                }
            response = requests.put(url,data=image,headers=headers)
            data=response.json()
            try: 
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/blogs-payment/{request.user.username}/{image}"
                    payment.save()
            except:
                pass  
            payment.data=json.dumps(price_data)
            payment.save()
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
            return redirect(reverse("accounts:blog_payment"))
        else:
            messages.error(request,"invalid form")
    return redirect(reverse("blogs:payment",kwargs={"id":price.id}))

@login_required(login_url="accounts:login")
@complete_user_data
@check_user_status
def payment_pricing(request,id):
    price=get_object_or_404(Prices,id=id)
    form=PaymentForm(request.POST or None,request.FILES or None)
    context={'price':price,"form":form}
    return render(request,"blog_payment.html",context)



from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID=os.environ["CLIENT_ID"] # paypal
CLIENT_SECRET=os.environ["CLIENT_SECRET"] # paypl

@login_required(login_url="accounts:login")
@check_user_status
@complete_user_data
def paypal_create(request,id):
    if request.method =="POST":
        try:
            price=get_object_or_404(Prices,id=id)
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
                            "value": price.price,
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value":  price.price
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
def paypal_capture(request,order_id,price_id):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']

        price=get_object_or_404(Prices,id=price_id)
        try:
            if data["status"] == "COMPLETED" and request.user.vip == False:
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                now= datetime.date.today()
                payment=Blog_Payment.objects.create(method="Paypal",
                transaction_number=transaction,type=1,amount=price.price,status="pending",user=request.user,created_at=now)
                if price.get_duration() == '3 month':
                    price_data={"duration":3,"type":"agartha"}
                    payment.expired_at= now + datetime.timedelta(days=30*3)
                if price.get_duration() == '6 month':
                    price_data={"duration":6,"type":"agartha"}
                    payment.expired_at= now + datetime.timedelta(days=30*6)
                if price.get_duration() == '12 month':
                    price_data={"duration":12,"type":"agartha"}
                    payment.expired_at= now + datetime.timedelta(days=365)
                payment.data=json.dumps(price_data)
                payment.save()
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
def blogs_type(request,type):
    blogs=Blog.objects.filter(status="approved",blog_type=type,domain_type=1)
    paginator = Paginator(blogs, 1) # Show 25 contacts per pag.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj,"slider":blog_slider(),"type":type,
            "recent_blogs":recent_blogs(),"recent_categories":recent_categories()}
    return render(request,"blog_type.html",context)

def random_integer_generator(size = 8, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

