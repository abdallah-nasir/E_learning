from django.urls import path,include
from . import views
from .views import *
app_name="Consultant"
urlpatterns = [
path("",views.home,name="home"),
path("teacher/<str:slug>/",views.get_consultant,name="get_consultant"),
path("checkout/<str:slug>/",views.checkout,name="checkout"),
path("western/<str:teacher>/",views.western_payment,name="western_payment"),
path("paypal/<str:teacher>/",views.paypal_payment,name="paypal_payment"),
path("payment/<str:teacher>/create/",views.paypal_create,name="paypal_create"),
path("paypal/<str:teacher_id>/capture/<str:order_id>/<str:user>/<str:user_data_form>/",views.paypal_capture,name="paypal_capture"),

path("paymob/<str:teacher>/",views.paymob_payment,name="paymob_payment"),
# path("ajax/teacher/",views.teacher_ajax,name="teacher_table"),
# path("ajax/teacher/table",views.teacher_ajax_table,name="teacher_ajax_table"),
path("test/<int:teacher>/",views.paymob_payment,name="test"),
] 
