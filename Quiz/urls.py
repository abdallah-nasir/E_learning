from django.urls import path,include
from . import views 
from .views import *
app_name="Quiz"


urlpatterns = [
    path("course/<str:course>/<str:question>/",views.quiz,name="home"),
    path("result/<str:slug>/",views.quiz_result,name="result"),

     


] 
