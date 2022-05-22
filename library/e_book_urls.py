from django.urls import path,include
from . import e_book as views
app_name="library"
urlpatterns = [
#### movies
    # path("",views.books,name="book"),
    path("book/<str:slug>/",views.single_book,name="single_book"),
    path("read/<str:slug>/",views.read_book,name="read_book"),
    path("comments/create/<str:slug>/",views.comment,name="comment"),
    path("payment/<str:slug>/",views.book_payment,name="e_book_payment"),
    path("paypal/create/<int:id>/",views.paypal_create,name="paypal_create"),
    path("paypal/capture/<str:order_id>/<str:track_id>/",views.paypal_capture,name="paypal_capture"),
    path("western/create/<str:slug>/",views.western_payment,name="western_payment"),
    path("bank/create/<str:slug>/",views.bank_payment,name="bank_payment"),


]  