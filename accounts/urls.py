from django.urls import path,include
from . import views
from .views import *
app_name="accounts"
urlpatterns = [
path("logout/",views.logout_view,name="logout"),
path("validate/teacher/",views.check_teacher_form,name="validate_teacher"),
path("profile/",views.account_info,name="account_info"),
path("profile/blog/payment/",views.blog_payment,name="blog_payment"),
path("profile/course/payment/",views.course_payment,name="course_payment"),
path("profile/consultant/payment/",views.account_info,name="consultant_payment"),
# path("profile/blogs/",views.blogs,name="blogs"),
path("profile/courses/",views.courses,name="courses"),
path("profile/events/",views.events,name="events"),

]