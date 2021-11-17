from django.urls import path,include
from . import views
from .views import *
app_name="Blogs"
urlpatterns = [
path("",views.home,name="blogs"),
path("<str:slug>/",views.single_blog,name="blog"),
path("search/",views.blog_search,name="search"),

path("add-blog-comment/<str:id>/",views.blog_comment,name="add_blog_comment"),
path("add-blog-comment-reply/<str:id>/<str:reply>/",views.blog_comment_reply,name="add_blog_comment_reply"),
# path("search/",views.global_search,name="global_search"),
]