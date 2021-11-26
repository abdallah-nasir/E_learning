from django.db.models.query_utils import Q
from django.shortcuts import render,redirect,reverse
from .models import *
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .forms import *
from .decorators import *
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
from django.core.cache import cache
# Create your views here.
class FailedJsonResponse(JsonResponse):
    def __init__(self, data):
        super().__init__(data)
        self.status_code = 400

def global_search(request):
    qs=request.GET.get("qs")
    courses=Course.objects.filter(Q(name__icontains=qs,approved=True) | Q(details__icontains=qs,approved=True) | Q(branch__name__icontains=qs,approved=True) | Q(branch__category__name__icontains=qs,approved=True) | Q(Instructor__username=qs,approved=True)).distinct() 
    if len(courses) == 0:
        page_obj=[]
        qs=None
    else:
        paginator = Paginator(courses, 8) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    context={"results":courses}
    return render(request,"global_search.html",context)

def course_search(request):
    qs=request.GET.get("qs")
    course=Course.objects.filter(Q(name__icontains=qs,approved=True) | Q(details__icontains=qs,approved=True) | Q(branch__name__icontains=qs,approved=True) | Q(branch__category__name__icontains=qs,approved=True)).distinct() 

    if len(course) == 0:
        page_obj=[]
        qs=None
    else:
        paginator = Paginator(course, 8) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,"course_search.html",{"course":page_obj,"qs":qs})

def home(request):
    events=Events.objects.filter(approved=True).order_by("-date")[:5]
    courses=Course.objects.filter(approved=True).order_by("-id")[0:5]
    teachers=User.objects.filter(account_type="teacher").order_by("?")[:4]
    context={"events":events,"courses":courses,"teachers":teachers}
    return render(request,"home.html",context)
    
def courses(request):
    course=Course.objects.filter(approved=True)
    paginator = Paginator(course, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"course":page_obj}
    return render(request,"courses.html",context)

def branch(request,slug):
    branch=get_object_or_404(Branch,slug=slug)
    course=Course.objects.filter(branch=branch,approved=True)
    paginator = Paginator(course, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"course":page_obj,"branch":branch}
    return render(request,"branch.html",context)

videos_api="x80ZObZyzzTqvuG676i2EBCdN4NgnTfQ6LGIyB13tfePqUGeO2L2DVIWwyshEZ8W"
def single_course(request,slug):
    course=get_object_or_404(Course,slug=slug,approved=True)
    payment_form=PaymentMethodForm()
    form=ReviewForm(request.POST or None)
    print(request.user.username)
    if request.method == "POST":
        if request.user.is_authenticated:
            instance=form.save(commit=False)
            if form.is_valid():
                if Reviews.objects.filter(user=request.user,course=course).exists():
                    messages.error(request,"you already submitted to the course")
                    return redirect(reverse("home:course",kwargs={"slug":course.slug}))
                else:
                    instance.user=request.user
                    instance.course=course
                    instance.save()
                    course.reviews.add(instance)
                    course.save()
                    messages.success(request, 'thank you for your opinion')
        else:
            messages.error(request, 'login first')

    context={"course":course,"form":form,"payment_form":payment_form} 
    return render(request,"course-single.html",context)

def videos(request,course,slug):
    video=get_object_or_404(Videos,slug=slug)
    if not request.user in video.my_course.students.all():
        messages.error(request,"sorry you should buy course first")
        return redirect(reverse("home:course",kwargs={"slug":video.my_course.slug}))
    else:
        if request.method == "POST":
            if request.user.is_authenticated:
                if Reviews.objects.filter(user=request.user,course=video.my_course).exists():
                    messages.error(request,"you already submitted to the course")
                    return redirect(reverse("home:video",kwargs={"course":course,"slug":video.slug}))
                rate=request.POST.get("rate")
                review=request.POST.get("review")
                print(rate,review)
                if rate and review:
                    if 5 >= int(rate) >= 1:
                        my_review=Reviews.objects.create(user=request.user,review=review,
                            rate=int(rate),course=video.my_course)
                        messages.success(request, 'thank you for your opinion')
                        video.my_course.reviews.add(my_review)
                        video.my_course.save()
                    else:
                        messages.error(request,f'your rate must be between 1 To 5')
                else:
                    messages.error(request,f'invalid Rate / Review')
            else:
                messages.error(request, 'login first')
    context={"video":video,"course":video.my_course}
    return render(request,"video.html",context)

def events(request):
    events=Events.objects.filter(approved=True)
    paginator = Paginator(events, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"events":page_obj}    
    return render(request,"events.html",context)

def event_single(request,slug):
    event=get_object_or_404(Events,slug=slug,approved=True)
    context={"event":event}
    return render(request,"event_single.html",context)

def teachers(request):
    teahcers=User.objects.filter(account_type="teacher",is_active=True)
    paginator = Paginator(teahcers, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"teachers":page_obj}
    return render(request,"teachers.html",context)

def teacher_single(request,slug):
    teacher=get_object_or_404(User,slug=slug)
    courses=Course.objects.filter(Instructor=teacher,approved=True)
    reviews=Teacher_review.objects.filter(teacher=teacher).order_by("-id")
    if request.method == "POST":
        if request.user.is_authenticated:
            if not Teacher_review.objects.filter(user=request.user,teacher=teacher).exists():
                    rate=request.POST.get("rate")
                    review=request.POST.get("review")
                    print(rate,review)
                    if rate and review:
                        if 5 >= int(rate) >= 1:
                            my_review=Teacher_review.objects.create(user=request.user,review=review,
                                        rate=int(rate),teacher=teacher)
                            messages.success(request, 'thank you for your opinion')
                        else:
                            messages.error(request,f'your rate must be between 1 To 5')
                    else:
                        messages.error(request,f'invalid Rate / Review')
 
                            
            else:
                messages.error(request,f'you already submitted your review with Teacher/{teacher.first_name.title()}')
        else:
            messages.error(request, 'login first')

    context={"teacher":teacher,"courses":courses,"reviews":reviews}
    return render(request,"teachers-single.html",context)

def about(request):
    context={}
    return render(request,"about.html",context)


   
def category(request,slug):
    blogs=Blog.objects.filter(category__slug=slug)
    categories=Category.objects.all()
    if len(blogs) == 0:
        category_name=[]
        page_obj=None
    else:
        category_name=blogs.first().category.name
        paginator = Paginator(blogs, 8) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj,"categories":categories,"category_name":category_name,"slug":slug,"popular":popular_blogs()}
    return render(request,"category.html",context)

    


def shops(request):
    context={}   
    return render(request,"shops.html",context)

def shop(request):
    context={}
    return render(request,"shop.html",context)


def contact(request):
    if request.method == "POST":
        name=request.POST["name"]
        email=request.POST["email"]
        subject=request.POST["subject"]
        message=request.POST["message"]
        send_mail( 
    subject,
    f"from {email} \n {message}",
    email,
    [settings.EMAIL_HOST_USER],
    fail_silently=False,
)
        messages.success(request,"thank you for your message")
    context={}
    return render(request,"contact.html",context)
@login_required()
def wishlist(request,slug):
    wishlist,created=Wishlist.objects.get_or_create(user=request.user)
    if len(wishlist.course.all()) == 0:
        messages.error(request,"your cart is empty")
        return redirect(reverse("home:home"))
    paginator = Paginator(wishlist.course.all(), 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"course":page_obj} 
    return render(request,"wishlist.html",context)

def wishlist_remove(request):
    if request.user.is_authenticated:
        print("ajax")
        id=request.GET["id"]
        my_course=get_object_or_404(Course,id=id)
        try:
            wishlist,created=Wishlist.objects.get_or_create(user=request.user)
            wishlist.course.remove(my_course)
            my_course.likes -=1
            my_course.save()
            return JsonResponse({"id":my_course.id,"shop":wishlist.course.count(),"count":wishlist.course.count()})

        except: 
            return FailedJsonResponse({"message":"invalid id"})
    else:
        print("here")
        return FailedJsonResponse({"message":"error message"})

# @login_required()
def wishlist_add(request):
    if request.user.is_authenticated:
        id=request.GET["id"]
        my_course=get_object_or_404(Course,id=id)
        try:
            wishlist,created=Wishlist.objects.get_or_create(user=request.user)
            print("ajax")
            if not my_course in wishlist.course.all():
                wishlist.course.add(my_course)
                my_course.likes +=1
                my_course.save()
                print("added")
                return JsonResponse({"color":"yellow","id":my_course.id,"shop":wishlist.course.count(),"count":my_course.likes})
            else:
                wishlist.course.remove(my_course)
                my_course.likes -=1
                my_course.save()
                return JsonResponse({"color":"white","id":my_course.id,"shop":wishlist.course.count(),"count":my_course.likes})
        except: 
            return FailedJsonResponse({"message":"invalid id"})
    else:
        print("here")
        return FailedJsonResponse({"message":"error message"})

def checkout(request):
    return render(request,"checkout.html")
from allauth.account.forms import SignupForm,LoginForm

def test(request):   
    return render(request,"test.html")
        

#######################################
#payment
def payment_method_ajax(request):
    course_id=request.POST.get("ajax_course")
    print(course_id)
    course=get_object_or_404(Course,id=course_id)
    payment_form=PaymentMethodForm(request.POST or None,request.FILES or None)
    my_method=None
    if request.is_ajax():     
        my_method=request.POST.get("payment_method")
        print(my_method)
        if payment_form.is_valid():
            return JsonResponse({"payment":my_method})
        else:
            return FailedJsonResponse({"payment":payment_form.errors})

@login_required()
@check_if_user_in_course
@check_if_user_in_pending_payment
def payment_method_create(request,course):
    course=get_object_or_404(Course,slug=course)
    if request.method == 'POST':
        payment_form=PaymentMethodForm(request.POST , request.FILES)
        if payment_form.is_valid():
            method=payment_form.cleaned_data["payment_method"]
            image=payment_form.cleaned_data["image"]
            number=payment_form.cleaned_data["number"]
            Payment.objects.create(user=request.user,method=method,
            payment_image=image,transaction_number=number,course=course,       
                pending=True)
            msg = EmailMessage(subject="order confirm", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[request.user.email])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            messages.success(request,"We Have sent an Email, Please check your Inbox")
            return redirect(reverse("home:course",kwargs={"slug":course.slug}))
        else:
            print("invalid")
            for i in payment_form.errors.values():
                messages.error(request,i)
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            # return redirect(reverse("home:course",kwargs={"slug":course.slug}))


from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalcheckoutsdk.core import SandboxEnvironment,PayPalHttpClient
CLIENT_ID="AZDbi4r4DSUE9nyMkO0QQjoMwgpfLjpKV7oYbbx_OlumnJM3xtNNoCkHAkevpHfunFJAaqCUSBvnLJez" # paypal
CLIENT_SECRET="ED45Xje6Z5SyKQe3EPTblfvM9gOidJTXq342B602AGNi4stk4i9wduEtYTbPzcGBDhTVAZ0cmbZg5b2w" # paypl
@login_required()
@check_if_user_in_course
@check_if_user_in_pending_payment
def create(request,course):
    if request.method =="POST":
        try:
            course=get_object_or_404(Course,slug=course)
           
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
                            "value": course.price,
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value":  course.price
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
            print("except")
            data={}
            return JsonResponse(data)
    else:
        print("not here")
        return JsonResponse({'details': "invalid request"})         

@login_required()
def capture(request,order_id,course):       
    if request.method=="POST": 
        capture_order = OrdersCaptureRequest(order_id)
        environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        client = PayPalHttpClient(environment)
        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        print(data)
        payment=Payment.objects.create(user=request.user,course_id=course,pending=True)
        try:
            if data["status"] == "COMPLETED" and payment.ordered == False:
                for i in data["purchase_units"]:
                    for b in i['payments']["captures"]:
                        transaction=b["id"]
                payment.transaction_number=transaction
                payment.method ="Paypal"
                payment.save()
                # payment.course.students.add(request.user)     i pussed adding student automaticly
                # payment.course.save()
                messages.add_message(request, messages.SUCCESS,"We Have sent an Email,Please check your Inbox")
                # msg_html = render_to_string("email_order_confirm.html",{"order":order})
                msg = EmailMessage(subject="order confirm", body="thank you for your payment", from_email=settings.EMAIL_HOST_USER, to=[payment.user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                return JsonResponse({"status":1})
            else:
                return JsonResponse({"status":0})
        except:
            return JsonResponse({"status":0})


def success(request):   
    return render(request,"success.html")
        
def failed(request):   
    return render(request,"failed.html")
##########################

def faqs(request):
    return render(request,"faqs.html")

    