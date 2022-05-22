from django.urls import path,include
from . import views
from .views import *

app_name="accounts"
urlpatterns = [
path("logout/",views.logout_view,name="logout"),
path("signup/",CustomSignupView.as_view(),name="signup"),
path("login/",CustomSigninView.as_view(),name="login"),
 
path("validate/teacher/",views.check_teacher_form,name="validate_teacher"),
path("",views.account_info,name="account_info"),
# path("code/reset/",views.code_reset,name="code"),

path("blog/payment/",views.blog_payment,name="blog_payment"),
path("course/payment/",views.course_payment,name="course_payment"),
path("consultant/payment/",views.consultant_payment,name="consultant_payment"),
path("movies/payment/",views.movies_payment,name="movies_payment"),
path("music/payment/",views.audio_payment,name="audio_payment"),
path("audio-books/payment/",views.audio_book_payment,name="audio_book_payment"),
path("e-books/payment/",views.e_book_payment,name="e_book_payment"),

# path("profile/blogs/",views.blogs,name="blogs"),
 
path("courses/",views.courses,name="courses"),
path("events/",views.events,name="events"),
path("consultants/",views.consultants,name="consultants"),
path("library/",views.library,name="library"),

path("edit/blog/payment/<str:id>/",views.edit_blog_payment,name="edit_blog_payment"),
path("edit/course/payment/<str:id>/",views.edit_course_payment,name="edit_course_payment"),
path("edit/consultant/payment/<str:id>/",views.edit_consultant_payment,name="edit_consultant_payment"),
path("edit/movies/payment/<str:slug>/<str:id>/",views.edit_movies_payment,name="edit_movies_payment"),
path("edit/audio-book/payment/<str:slug>/<str:id>/",views.edit_audio_book_payment,name="edit_audio_book_payment"),
path("edit/audio/payment/<str:slug>/<str:id>/",views.edit_audio_payment,name="edit_audio_payment"),
path("edit/e-book/payment/<str:slug>/<str:id>/",views.edit_e_book_payment,name="edit_e_book_payment"),



#refunds
path("refunds/consultant/<int:id>/",views.consultant_refund,name="consultant_refund"),
path("refunds/course/<int:id>/<str:slug>/",views.course_refund,name="course_refund"),
path("refunds/movies/<str:slug>/<int:id>/",views.movies_refund,name="movies_refund"),
path("refunds/music/<str:slug>/<int:id>/",views.music_refund,name="music_refund"), 
path("refunds/audio-book/<str:slug>/<int:id>/",views.audio_book_refund,name="audio_book_refund"), 
path("refunds/e-book/<str:slug>/<int:id>/",views.e_book_refund,name="e_book_refund"), 


]