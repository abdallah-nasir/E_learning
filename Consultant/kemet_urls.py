from django.urls import path,include
from . import kemet_views as views
from .kemet_views import *
app_name="Consultant"
urlpatterns = [
path("",views.home,name="home"),
path("teacher/<str:slug>/",views.get_consultant,name="get_consultant"),
path("checkout/<str:slug>/",views.checkout,name="checkout"),
path("western/<str:teacher>/",views.western_payment,name="western_payment"),
path("bank/payment/<str:teacher>/",views.bank_payment,name="bank_payment"),

path("payment/<str:teacher>/",views.payment,name="payment"),
path("paypal/create/<str:teacher>/create/",views.paypal_create,name="paypal_create"),
path("paypal/capture/<str:teacher_id>/<str:order_id>/<str:user>/<str:user_data_form>/",views.paypal_capture,name="paypal_capture"),
path("check/payment/<int:id>/",views.post_payment_data,name="post_payment_data"),

# path("ajax/teacher/",views.teacher_ajax,name="teacher_table"),
# path("ajax/teacher/table",views.teacher_ajax_table,name="teacher_ajax_table"),
# path("test/<int:teacher>/",views.paymob_payment,name="test"),
] 
