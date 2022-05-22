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
from E_learning.all_email import *

def get_library_home_data():
    audio_book=Audio_Book_Tracks.objects.filter(status="approved").order_by("-id")[:5]
    e_book=E_Book.objects.filter(status="approved").order_by("-id")[:6]
    context={"audio_books":audio_book,"e_books":e_book}
    return context

@login_required(login_url="accounts:login")
def search(request):
    categories=Category.objects.all()
    author=request.GET.get("author")
    type=request.GET.get("type")
    category=request.GET.get("category")
    language=request.GET.get("language")
    title=request.GET.get("title")
    translator=request.GET.get("translator")
    publisher=request.GET.get("publisher")
    isbn=request.GET.get("isbn")
    price=request.GET.get("price")
    all_filters={"status":"approved","category__id":category,"data__language":language,"name__icontains":title,"data__translator__icontains":translator,"data__publisher__icontains":publisher,"data__isbn":isbn,"price__range":(0,price)}
    new_filter={}
    for i in all_filters:
        if all_filters[i] != None and all_filters[i] != "" :
            new_filter[i] =all_filters[i]
    if type == "e-book":
        query=E_Book.objects.filter(**new_filter)
    else:
        query=Audio_Book_Tracks.objects.filter(**new_filter)
    context={"query":query,"type":type,"categories":categories}
    return render(request,"library/search.html",context)


@login_required(login_url="accounts:login")
def home(request):
    data=get_library_home_data()
    context={"data":data}
    return render(request,"library/home.html",context)
   
@login_required(login_url="accounts:login")
def books(request,slug):
    if slug == "audio-book":
        books=Audio_Book_Tracks.objects.filter(status="approved")
    elif slug == "e-book":
        books=E_Book.objects.filter(status="approved")
    else:
        return redirect(reverse("library:home"))
    categories=Category.objects.all()
    paginator = Paginator(books, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"books":page_obj,"slug":slug,"categories":categories}
    return render(request,"library/all-books.html",context)


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
@check_video_payment_western
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
            return redirect(reverse("library:movie_payment",kwargs={"slug":movie.slug}))


@login_required(login_url="accounts:login")
@check_user_is_kemet_vip
@check_video_payment_bank
def create_movie_bank_payment(request,slug):
    form=PaymentForm(request.POST or None ,request.FILES or None)
    movie=get_object_or_404(Movies,slug=slug,status="approved")
    if request.method == 'POST':
        if form.is_valid():
            now= datetime.date.today()
            image=form.cleaned_data["image"]
            number=form.cleaned_data["number"]
            payment=Library_Payment.objects.create(user=request.user,
            method="bank",content_id=movie.id,library_type=3,amount=movie.get_price(), transaction_number=number,status="pending",created_at=now)
            image_url=f"https://storage.bunnycdn.com/{storage_name}/movies-payment/{movie.slug}/{payment.user.username}/{image}"
            headers = {
                "AccessKey": Storage_Api, 
                "Content-Type": "application/octet-stream",
                }
            response = requests.put(image_url,data=image,headers=headers)
            data=response.json()
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

