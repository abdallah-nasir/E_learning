from django.shortcuts import render
from .models import *
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail,EmailMessage,get_connection
from .decorators import *

# Create your views here.
def get_library_home_data():
    audio_libraries=Library.objects.filter(type=3).order_by("-id")[:8]
    e_book_libraries=Library.objects.filter(type=4).order_by("-id")[:8]
    context={"audios":audio_libraries,"e_books":e_book_libraries}
    return context
@login_required(login_url="accounts:login")
def home(request):
    data=get_library_home_data()
    # paginator = Paginator(libraries, 9) 
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    context={"data":data}
    return render(request,"library/library_home.html",context)
   

@login_required(login_url="accounts:login")
def e_books(request):
    # paginator = Paginator(libraries, 9) 
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    context={}
    return render(request,"library/e_books.html",context)
   