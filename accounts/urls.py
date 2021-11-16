from django.urls import path,include
from . import views
from .views import *
app_name="accounts"
urlpatterns = [
path("logout/",views.logout_view,name="logout"),
path("validate/teacher/",views.check_teacher_form,name="validate_teacher"),

]