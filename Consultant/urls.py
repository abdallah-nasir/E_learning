from django.urls import path,include
from . import views
from .views import *
app_name="Consultant"
urlpatterns = [
path("",views.home,name="home"),
path("payment/<str:teacher>/",views.consultant_payment,name="consultant_payment"),
path("paypal/create/<str:teacher>/",views.paypal_create,name="paypal_create"),
path("paypal/capture/<str:order_id>/<str:teacher_id>/",views.paypal_capture,name="paypal_capture"),
path("ajax/paymob/<str:teacher>/",views.paymob_payment,name="paymob_payment"),
path("ajax/teacher/",views.teacher_ajax,name="teacher_table"),
path("ajax/teacher/table",views.teacher_ajax_table,name="teacher_ajax_table"),

] 