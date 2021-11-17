from django.urls import path,include
from . import views
from .views import *
app_name="Blogs"
urlpatterns = [
path("",views.home,name="blogs"),
# path("add-blog-comment/",views.blog_comment,name="add_blog_comment"),
# path("add-blog-comment-reply/",views.blog_comment_reply,name="add_blog_comment_reply"),
# path("blogs/search/",views.blog_search,name="blog_search"),
# path("search/",views.global_search,name="global_search"),
]