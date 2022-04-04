from django.urls import path,include
from . import audio_book as views
app_name="library"
urlpatterns = [
#### movies
    path("",views.audio,name="audios"),
    path("<str:slug>/",views.single_audio,name="single_audio"),
    path("comments/create/<str:slug>/",views.comment,name="comment"),
    path("payment/<str:slug>/",views.audio_payment,name="audio_payment"),
    path("paypal/create/<int:id>/",views.paypal_create,name="paypal_create"),
    path("paypal/capture/<str:order_id>/<str:track_id>/",views.paypal_capture,name="paypal_capture"),
    path("western/create/<str:slug>/",views.western_payment,name="western_payment"),
    path("bank/create/<str:slug>/",views.bank_payment,name="bank_payment"),


]  