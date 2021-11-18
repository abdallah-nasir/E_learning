from django.shortcuts import render

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



def home(request):
    blogs=Blog.objects.filter(approved=True)
    paginator = Paginator(blogs, 9) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj,"slider":blog_slider()}
    return render(request,"blogs.html",context)

@login_required()
@check_user_is_member
def single_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    comment_form=CommentForm(request.POST or None)
    viewers=blog.check_blog_viwers(request.user)
    categories=recent_categories()
    context={"blog":blog,"categories":categories,"comment_form":comment_form}
    return render(request,"blog.html",context)

def blog_search(request):
    qs=request.GET.get("search")
    blog=Blog.objects.filter(Q(name__icontains=qs,approved=True) | Q(details__icontains=qs,approved=True) | Q(category__name__icontains=qs,approved=True) |Q(tags__name__icontains=qs,approved=True)).distinct() 
    print(blog)
    if len(blog) == 0:
        qs=None
        page_obj=[]
    else:
        paginator = Paginator(blog, 9) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,"blog_search.html",{"blogs":page_obj,"qs":qs})

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
    else:
        messages.error(request,"You Should Sign in First")
    return redirect(reverse("blogs:blog",kwargs={"slug":instance.blog.slug}))


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
    else:
        messages.error(request,"You Should Sign in First")
    return redirect(reverse("blogs:blog",kwargs={"slug":instance.blog.slug}))
import datetime
@login_required()
def pricing(request):
    prices=Prices.objects.all()
 
    return render(request,"pricing.html",{'prices':prices})

@login_required()
@check_user_status
def payment_pricing(request,id):
    price=get_object_or_404(Prices,id=id)
    form=PaymentForm(request.POST or None,request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            if request.user.vip == False and not Blog_Payment.objects.filter(user=request.user,pending=True).exists():
                now= datetime.date.today()
                method=form.cleaned_data["payment_method"]
                image=form.cleaned_data["image"]
                number=form.cleaned_data["number"]
                payment=Blog_Payment.objects.create(user=request.user,
                method=method,payment_image=image, transaction_number=number,pending=True,created_at=now)
                if price.get_duration() == 'month':
                    payment.created_at = now
                    payment.expired_at= now + datetime.timedelta(days=30)
                else:
                    payment.expired_at= now + datetime.timedelta(days=365)
                payment.save()
                msg = EmailMessage(subject="Payment completed", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[payment.user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                messages.success(request,"We Have sent an Email,Please check your Inbox")
                return redirect(reverse("blogs:blogs"))
            else:
                messages.error(request,"our team will review your request")
                return redirect(reverse("blogs:blogs"))
        else:
            messages.error(request,"invalid form")
    context={'price':price,"form":form}
    return render(request,"blog_payment.html",context)



from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID="AZDbi4r4DSUE9nyMkO0QQjoMwgpfLjpKV7oYbbx_OlumnJM3xtNNoCkHAkevpHfunFJAaqCUSBvnLJez" # paypal
CLIENT_SECRET="ED45Xje6Z5SyKQe3EPTblfvM9gOidJTXq342B602AGNi4stk4i9wduEtYTbPzcGBDhTVAZ0cmbZg5b2w" # paypl

@login_required()
@check_user_status
def paypal_create(request,id):
    if request.method =="POST":
        try:
            price=get_object_or_404(Prices,id=id)
            if request.user.vip == True:
                messages.error(request,"You Already A Member")
                return redirect(reverse("blogs:blogs"))
            elif Blog_Payment.objects.filter(user=request.user,pending=True).exists():
                messages.error(request,"our team will review your request")
                return redirect(reverse("blogs:blogs"))
            else:
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

@login_required()
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
                payment=Blog_Payment.objects.create(method="Paypal",transaction_number=transaction,user=request.user,created_at=now)
                if price.get_duration() == 'month':
                    payment.expired_at= now + datetime.timedelta(days=30)
                else:
                    payment.expired_at= now + datetime.timedelta(days=365)
                payment.save()
                request.user.vip =True
                request.user.save()
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

        # try:
        #     payment=Payment.objects.get(id=course)
            
        #     msg_html = render_to_string("email_order_confirm.html",{"order":order})
        #     msg = EmailMessage(subject="order confirm", body=msg_html, from_email=settings.EMAIL_HOST_USER, to=[order.user.email])
        #     msg.content_subtype = "html"  # Main content is now text/html
        #     msg.send()
        # except:
        #     pass
        # messages.success(request,"")
        # messages.add_message(request, messages.INFO,data)
    # return redirect(reverse("home:test"))
