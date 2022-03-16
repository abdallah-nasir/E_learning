from django.urls import path,include
from . import views 
from .views import *

app_name="library"
urlpatterns = [
    path("",views.home,name="home"),
    path("e-books/",views.e_books,name="e_books"),


]