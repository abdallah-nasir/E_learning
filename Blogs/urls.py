from django.urls import path,include
from . import views
from .views import *
app_name="Blogs"
urlpatterns = [
path("",views.home,name="blogs"),
path("blog/<str:slug>/",views.single_blog,name="blog"),
path("search/",views.blog_search,name="search"),
path("pricing/",views.pricing,name="pricing"),
path("payment/<str:id>/",views.payment_pricing,name="payment"),
path("type/<str:type>/",views.blogs_type,name="blogs_type"),

#### blogs
path("add-blog-comment/<str:id>/",views.blog_comment,name="add_blog_comment"),
path("add-blog-comment-reply/<str:id>/<str:reply>/",views.blog_comment_reply,name="add_blog_comment_reply"),
##### Payment 
path("paypal/create/<str:id>/",views.paypal_create,name="paypal_create"),
path("paypal/capture/<str:order_id>/<str:price_id>/",views.paypal_capture,name="paypal_capture"),
path("ajax/paymob/<str:id>/",views.paymob_payment,name="paymob_payment"),

]