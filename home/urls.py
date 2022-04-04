from django.urls import path,include
from . import views 
from .views import *
app_name="home"
 
urlpatterns = [
path("",views.home,name="home"),
path("courses/",views.courses,name="courses"),
path("course/<str:slug>/",views.single_course,name="course"),
path("course/<str:course>/<str:slug>/",views.videos,name="video"),
path("courses/category/<str:slug>/",views.course_category,name="course_category"),
path("courses/branch/<str:slug>/",views.branch,name="branch"),
path("events/",views.events,name="events"),
path("event/<str:slug>/",views.event_single,name="event"),
path("teachers/",views.teachers,name="teachers"),
path("teacher/<str:slug>/",views.teacher_single,name="teacher"),
path("about-us/",views.about,name="about"),
path("terms/",views.terms,name="terms"),
path("privacy/",views.privacy,name="privacy"),
path("test/",views.test,name="test"),

path("faqs/",views.faqs,name="faqs"),
# path("shop/",views.shop,name="shop"),
path("contact-us/",views.contact,name="contact"),
#wishlist
path("cart/<str:slug>/",views.wishlist,name="cart"),
path("wishlist-add/",views.wishlist_add,name="wishlist_add"),
path("wishlist-remove/",views.wishlist_remove,name="wishlist_remove"),
#checkout
path("checkout/courses/<str:course>/",views.checkout,name="checkout"),
path("western/<str:course>/",views.western_payment,name="western_payment"),

path("payment/success/",views.success,name="success"),
path("payment/failed/",views.failed,name="failed"),   
path("bank/<str:course>/",views.bank_payment,name="bank_payment"),
path("create/<str:course>/",views.create,name="create"),
path("capture/<str:order_id>/<str:course>/",views.capture,name="capture"),

###### subscribe news
path("subscribe/",views.subscribe,name="subscribe"),
#search
path("courses/search/",views.course_search,name="course_search"),
path("search/",views.global_search,name="global_search"),

#blog comment and replies

  
]
