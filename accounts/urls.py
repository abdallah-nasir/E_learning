from django.urls import path,include
from . import views
from .views import *
app_name="accounts"
urlpatterns = [
path("logout/",views.logout_view,name="logout"),
path("validate/teacher/",views.check_teacher_form,name="validate_teacher"),
path("",views.account_info,name="account_info"),
path("blog/payment/",views.blog_payment,name="blog_payment"),
path("course/payment/",views.course_payment,name="course_payment"),
path("consultant/payment/",views.consultant_payment,name="consultant_payment"),
# path("profile/blogs/",views.blogs,name="blogs"),
path("courses/",views.courses,name="courses"),
path("events/",views.events,name="events"),
path("consultants/",views.consultants,name="consultants"),

path("edit/blog/payment/<str:id>/",views.edit_blog_payment,name="edit_blog_payment"),
path("edit/course/payment/<str:id>/",views.edit_course_payment,name="edit_course_payment"),
path("edit/consultant/payment/<str:id>/",views.edit_consultant_payment,name="edit_consultant_payment"),

]