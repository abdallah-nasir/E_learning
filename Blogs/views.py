from django.shortcuts import render
import os
# Create your views here.
from django.db.models.query_utils import Q
from django.shortcuts import render,redirect,reverse
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
from django.core.mail import send_mail,EmailMessage
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from datetime import datetime
from django.forms import ValidationError
from .decorators import *
import requests,string
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]  # PAYMOB
PAYMOB_FRAME=os.environ["PAYMOB_FRAME"]
PAYMOB_BLOG_INT=os.environ['PAYMOB_BLOG_INT']

@login_required(login_url="accounts:login")
def home(request):
    blog_data=cache.get("blog_data")
    if blog_data == None:
        data=get_blog_data()
        cache.set("blog_data",data,60*15)
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
    blog=Blog.objects.filter(Q(name__icontains=qs,status="approved") | Q(details__icontains=qs,status="approved") | Q(category__name__icontains=qs,status="approved") |Q(tags__name__icontains=qs,status="approved")).distinct() 
    print(blog)
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
    prices=Prices.objects.all()
 
    return render(request,"pricing.html",{'prices':prices})

@login_required(login_url="accounts:login")
@check_user_status
@check_blogs_payment_status
@complete_user_data
def payment_pricing(request,id):
    price=get_object_or_404(Prices,id=id)
    form=PaymentForm(request.POST or None,request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            if request.user.vip == False and not Blog_Payment.objects.filter(user=request.user,status="pending").exists():
                now= datetime.date.today()
                method=form.cleaned_data["payment_method"]
                image=form.cleaned_data["image"]
                number=form.cleaned_data["number"]
                payment=Blog_Payment.objects.create(user=request.user,
                method=method,payment_image=image, transaction_number=number,status="pending",created_at=now)
                if price.get_duration() == 'monthly':
                    payment.created_at = now
                    payment.expired_at= now + datetime.timedelta(days=30*6)
                else:
                    payment.expired_at= now + datetime.timedelta(days=365)
                payment.save()
                msg = EmailMessage(subject="Payment completed", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[payment.user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                messages.success(request,"We Have sent an Email,Please check your Inbox")
                return redirect(reverse("blogs:blogs"))
            else:
                messages.error(request,"ou have a pending request ,our team will review your request")
                return redirect(reverse("blogs:blogs"))
        else:
            messages.error(request,"invalid form")
    context={'price':price,"form":form}
    return render(request,"blog_payment.html",context)



from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID=os.environ["CLIENT_ID"] # paypal
CLIENT_SECRET=os.environ["CLIENT_SECRET"] # paypl

@login_required(login_url="accounts:login")
@check_user_status
@check_blogs_payment_status
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
            # print(data)
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
        print(data)

        price=get_object_or_404(Prices,id=price_id)
        try:
            if data["status"] == "COMPLETED" and request.user.vip == False:
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                now= datetime.date.today()
                payment=Blog_Payment.objects.create(method="Paypal",
                transaction_number=transaction,status="pending",user=request.user,created_at=now)
                if price.get_duration() == 'monthly':
                    payment.expired_at= now + datetime.timedelta(days=30*6)
                else:
                    payment.expired_at= now + datetime.timedelta(days=365)
                payment.save()
                messages.add_message(request, messages.SUCCESS,"We Have sent an Email,Please check your Inbox")
                # msg_html = render_to_string("email_order_confirm.html",{"order":order})
                msg = EmailMessage(subject="Payment completed", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[payment.user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                return JsonResponse({"status":1})
            else:
                return JsonResponse({"status":0})
        except:
            return JsonResponse({"status":0})

@login_required(login_url="accounts:login")
def blogs_type(request,type):
    blogs=Blog.objects.filter(status="approved",blog_type=type)
    paginator = Paginator(blogs, 1) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj,"slider":blog_slider(),"type":type,
            "recent_blogs":recent_blogs(),"recent_categories":recent_categories()}
    return render(request,"blog_type.html",context)

def random_integer_generator(size = 8, chars = string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url="accounts:login")
@check_user_status
@complete_user_data
def paymob_payment(request,id):
    if request.is_ajax():     
        # return JsonResponse({"frame":PAYMOB_FRAME,"token":123})
        prices=Prices.objects.get(id=id)
        merchant_order_id=request.user.id + int(random_integer_generator())
        url_1 = "https://accept.paymob.com/api/auth/tokens"
        data_1 = {"api_key": PAYMOB_API_KEY}
        r_1 = requests.post(url_1, json=data_1)
        token = r_1.json().get("token")
        print(token)
        data_2 = {
            "auth_token": token,
            "delivery_needed": "false",
                "amount_cents":prices.price * 100,
                "currency": "EGP",
                "merchant_order_id": merchant_order_id,  # 81

                "items": [
        {
            "name": prices.id,
            "amount_cents": prices.price * 100,
            "description": "blogs",
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
            "amount_cents": prices.price * 100,
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
            "integration_id": PAYMOB_BLOG_INT,
            "lock_order_when_paid": "true"
        }
        url_3 = "https://accept.paymob.com/api/acceptance/payment_keys"
        r_3 = requests.post(url_3, json=data_3)
        payment_token = (r_3.json().get("token"))
        print(payment_token)
        return JsonResponse({"frame":PAYMOB_FRAME,"token":payment_token})

