from django.urls import path,include
from . import views 
from .views import *
app_name="Dashboard"

urlpatterns = [
path("",views.home,name="home"),
path("blog/payment/",views.blog_payment,name="blog_payment"),
path("course/payment/",views.course_payment,name="course_payment"),
path("consultant/payment/",views.consultant_payment,name="consultant_payment"),
### blogs
path("blogs/",views.blogs,name="blogs"),
path("demo/blog/<str:slug>/",views.show_demo_blog,name="show_demo_blog"),

path("add/blogs/",views.add_blog,name="add_blog"),
path("edit/blogs/<str:slug>/",views.edit_blog,name="edit_blog"),
path("delete/blogs/<str:slug>/",views.delete_blog,name="delete_blog"),
path("delete/image/blogs/<str:id>/",views.delete_blog_image,name="delete_blog_image"),
path("delete/videos/blogs/<str:id>/",views.delete_blog_video,name="delete_blog_video"),


#### course
path("courses/",views.courses,name="courses"),
path("videos/",views.videos,name="videos"),
path("delete/videos/<str:slug>/",views.delete_videos,name="delete_videos"),

path("add/course/",views.add_course,name="add_course"),
path("add/video/<str:slug>/",views.add_video,name="add_video"),
path("edit/courses/<str:slug>/",views.edit_course,name="edit_course"),
   
#events
path("events/",views.events,name="events"),
path("add/events/",views.add_event,name="add_event"),
path("edit/events/<str:id>/",views.edit_event,name="edit_event"),
path("delete/events/<str:id>/",views.delete_event,name="delete_event"),
path("start/events/<str:slug>/",views.start_event,name="start_event"),
path("finish/events/<str:id>/",views.finish_event,name="finish_event"),

# #quiz Questions
path("quiz/<str:slug>/",views.quiz,name="quiz"),
path("add/quiz/<str:slug>/",views.add_quiestions,name="add_quiestions"),
path("edit/question/<str:course>/<str:slug>/",views.edit_quiestions,name="edit_quiestions"),
path("delete/question/<str:slug>/<str:id>/",views.delete_question,name="delete_question"),
# #quiz Answers
path("add/answer/<str:course>/<str:slug>/",views.add_answer,name="add_answer"),
path("edit/answer/<str:course>/<str:slug>/",views.edit_answer,name="edit_answer"),
path("delete/answer/<str:slug>/<str:id>/",views.delete_answer,name="delete_answer"),
# teachers
path("teachers/",views.teachers,name="teachers"),
#approve
path("approves/",views.approve,name="approve"),
path("approve/<str:id>/",views.approve_content,name="approve_content"),
#aprove
path("reject/<str:id>/",views.reject,name="reject"),

#news
path("news/",views.news,name="news"),
path("news/edit/<str:id>/",views.edit_news,name="edit_news"),
path("news/add/",views.add_news,name="add_news"),
path("news/delete/<str:id>/",views.delete_news,name="delete_news"),



]  
