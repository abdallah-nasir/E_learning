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
Storage_Api=os.environ["Storage_Api"]
storage_name=os.environ["storage_name"]
library_id=os.environ["library_id"]
storage_name=os.environ["storage_name"]
agartha_cdn=os.environ['agartha_cdn']
PAYMOB_API_KEY = os.environ["PAYMOB_API_KEY"]  # PAYMOB
PAYMOB_FRAME=os.environ["PAYMOB_FRAME"]
PAYMOB_BLOG_INT=os.environ['PAYMOB_BLOG_INT']
PAYMENT_EMAIL_USERNAME = os.environ['PAYMENT_EMAIL_USERNAME']
PAYMENT_EMAIL_PASSWORD = os.environ['PAYMENT_EMAIL_PASSWORD']
PAYMENT_EMAIL_PORT = os.environ['PAYMENT_EMAIL_PORT']
SUPPORT_EMAIL_HOST = os.environ['SUPPORT_EMAIL_HOST']
PAYMENT_MAIL_CONNECTION = get_connection(
host= SUPPORT_EMAIL_HOST, 
port=PAYMENT_EMAIL_PORT, 
username=PAYMENT_EMAIL_USERNAME, 
password=PAYMENT_EMAIL_PASSWORD, 
use_tls=False
) 
TASK_NOTIFICATION_EMAIL_USERNAME=os.environ['TASK_NOTIFICATION_EMAIL_USERNAME']
TASK_NOTIFICATION_EMAIL_PASSWORD=os.environ['TASK_NOTIFICATION_EMAIL_PASSWORD']
TASK_NOTIFICATION_EMAIL_HOST=os.environ["TASK_NOTIFICATION_EMAIL_HOST"]
TASK_NOTIFICATION_EMAIL_PORT=os.environ["TASK_NOTIFICATION_EMAIL_PORT"]
TASK_NOTIFICATION_EMAIL_CONNECTION=get_connection(
host= TASK_NOTIFICATION_EMAIL_HOST, 
port=TASK_NOTIFICATION_EMAIL_PORT, 
username=TASK_NOTIFICATION_EMAIL_USERNAME, 
password=TASK_NOTIFICATION_EMAIL_PASSWORD, 
use_tls=False
)
from paypalcheckoutsdk.orders import OrdersCreateRequest 
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID=os.environ["CLIENT_ID"] # paypal
CLIENT_SECRET=os.environ["CLIENT_SECRET"] # paypl
# Create your views here.
def send_mail_approve(request,user,body,subject):
    msg = EmailMessage(   
        subject=subject,
        body=body,
        from_email=TASK_NOTIFICATION_EMAIL_USERNAME,
        to=[TASK_NOTIFICATION_EMAIL_USERNAME],
        reply_to=[user],
        connection=TASK_NOTIFICATION_EMAIL_CONNECTION
        )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    return True

def get_home_cache_data():
    audios=Audio_Tracks.objects.filter(status="approved").select_related("user").order_by("-id")[:13]
    artists=Artist.objects.filter(status="approved").select_related("user")[:8]
    last_songs=Music.objects.all().select_related("track").order_by("-id")[:6]
    context={"audios":audios,"artists":artists,"music":last_songs}
    return context


@login_required(login_url="accounts:login")
def search(request):
    qs=request.GET.get("qs")
    type=False
    query=False
    if qs:
        type=request.GET.get("type")
        if type == "4":
            query=Audio_Tracks.objects.filter(Q(name__icontains=qs) |Q(music__name=qs) | Q(category__name__icontains=qs)).prefetch_related("music").distinct()
        if type == "5":
            query=Blog.objects.filter(Q(blog_type="audio",name__icontains=qs) | Q(blog_type="audio",category__name__icontains=qs)).select_related("user").distinct()
        if type == "3":
            query=Movies.objects.filter(Q(name__icontains=qs) | Q(user__username__icontains=qs) | Q(category__name__icontains=qs)).select_related("user").distinct()
        if type == "6":
            query=Artist.objects.filter(Q(user__username__icontains=qs) | Q(user__first_name__icontains=qs)).select_related("user").distinct()
        else:
            query=Audio_Tracks.objects.filter(Q(name__icontains=qs) |Q(music__name=qs) | Q(category__name__icontains=qs)).prefetch_related("music").distinct()
        print(query)
    # if query:
    #     if 
    context={"qs":qs,"query":query,"type":type}
    return render(request,"library/audio/search.html",context)
@login_required(login_url="accounts:login")
def home(request):
    data=get_home_cache_data()
    context={"data":data}
    return render(request,"library/audio/home.html",context)


@login_required(login_url="accounts:login")
def audio(request):
    tracks=Audio_Tracks.objects.filter(status="approved").prefetch_related("music")
    paginator = Paginator(tracks, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"tracks":page_obj}
    return render(request,"library/audio/audios.html",context)

@login_required(login_url="accounts:login")
def single_audio(request,slug):
    track=get_object_or_404(Audio_Tracks,slug=slug,status="approved")
    check_user=track.check_user_in(request.user.id)
    context={"track":track,"data":track.get_cache_data(),"check_user":check_user}
    return render(request,"library/audio/single_track.html",context)
 
@login_required(login_url="accounts:login")
def comment(request,slug):
    track=get_object_or_404(Audio_Tracks,slug=slug,status="approved")
    form=CommentsForm(request.POST)
    if Comments.objects.filter(user=request.user,library=2,content_id=track.id).select_related("user").exists():
        messages.error(request,"you already have a comment for this track")
    else:
        if form.is_valid():
            comment=form.cleaned_data.get("comment")
            comment=Comments.objects.create(user=request.user,library=2,content_id=track.id,comment=comment)
            track.comments.add(comment)
            track.save()
            messages.success(request,"thank you for your review")
    return redirect(reverse('library:single_audio',kwargs={"slug":slug}))


@login_required(login_url="accounts:login")
def artists(request):
    artists=Artist.objects.filter(status="approved").select_related("user")
    paginator = Paginator(artists, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"artists":page_obj}
    return render(request,"library/audio/artists.html",context)

@login_required(login_url="accounts:login")
def single_artist(request,slug):
    artist=get_object_or_404(Artist,user__slug=slug)
    context={"artist":artist}
    return render(request,"library/audio/artist.html",context)

@login_required(login_url="accounts:login")
def blog_audios(request):
    blogs=Blog.objects.filter(blog_type="audio",status="approved").select_related("user")
    paginator = Paginator(blogs, 1) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj}
    return render(request,"library/audio/blog_audios.html",context)




@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_audio_payment_page
def audio_payment(request,slug):
    track=get_object_or_404(Audio_Tracks,slug=slug,status="approved")
    if int(track.get_price()) <= 0:
        return redirect(reverse("library:single_audio",kwargs={"slug":slug}))
    context={"track":track}
    return render(request,"library/audio/payment.html",context)

@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_audio_payment_western
def create_audio_western_payment(request,slug):
    form=PaymentForm(request.POST or None ,request.FILES or None)
    track=get_object_or_404(Audio_Tracks,slug=slug,status="approved")
    if request.method == 'POST':
        if form.is_valid():
            now= datetime.date.today()
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]
            payment=Library_Payment.objects.create(user=request.user,
            method="Western Union",content_id=track.id,library_type=2,amount=track.get_price(), transaction_number=number,status="pending",created_at=now)
            image_url=f"https://storage.bunnycdn.com/{storage_name}/music-payment/{track.slug}/{payment.user.username}/{image}"
            headers = {
                "AccessKey": Storage_Api, 
                "Content-Type": "application/octet-stream",
                }
            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
            print(data) 
            try:
                if data["HttpCode"] == 201:
                    payment.payment_image = f"https://{agartha_cdn}/music-payment/{track.slug}/{payment.user.username}/{image}"
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
            return redirect(reverse("accounts:music_payment"))
        else:
            messages.error(request,"invalid form")
            print(form.errors)
            return redirect(reverse("library:music_payment",kwargs={"slug":track.slug}))



@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@complete_user_data
def paypal_create(request,id):
    if request.method =="POST":
        try:
            track=get_object_or_404(Audio_Tracks,id=id,status="approved")
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
        track=get_object_or_404(Audio_Tracks,id=track_id)
        try:
            if data["status"] == "COMPLETED":
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                now= datetime.date.today()
                payment=Library_Payment.objects.create(method="Paypal",
                transaction_number=transaction,content_id=track.id,amount=track.get_price(),status="pending",user=request.user,created_at=now,library_type=2)
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

