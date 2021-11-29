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

path("courses/",views.courses,name="courses"),
path("add/blogs/",views.add_blog,name="add_blog"),
path("edit/blogs/<str:slug>/",views.edit_blog,name="edit_blog"),
path("delete/blogs/<str:slug>/",views.delete_blog,name="delete_blog"),
#### course
path("add/course/",views.add_course,name="add_course"),
path("add/video/<str:slug>/",views.add_video,name="add_video"),
path("edit/courses/<str:slug>/",views.edit_course,name="edit_course"),
   
#events
path("events/",views.events,name="events"),
path("add/events/",views.add_event,name="add_event"),
path("edit/events/<str:id>/",views.edit_event,name="edit_event"),
path("delete/events/<str:id>/",views.delete_event,name="delete_event"),
 
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




]  
