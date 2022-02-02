from django.urls import path,include
from . import views 
from .views import *
app_name="Dashboard"

urlpatterns = [
path("",views.home,name="home"),
path("blog/payment/",views.blog_payment,name="blog_payment"),
path("course/payment/",views.course_payment,name="course_payment"),
path("consultant/payment/",views.consultant_payment,name="consultant_payment"),

# edits
path("blog/payment/edit/<int:id>/",views.edit_blog_payment,name="edit_blog_payment"),
path("course/payment/edit/<int:id>/",views.edit_course_payment,name="edit_course_payment"),
path("consultant/payment/edit/<int:id>/",views.edit_consultant_payment,name="edit_consultant_payment"),

### blogs
path("blogs/",views.blogs,name="blogs"),
path("demo/blog/<str:slug>/",views.show_demo_blog,name="show_demo_blog"),

path("add/blogs/",views.add_blog,name="add_blog"),
path("edit/blogs/<str:slug>/",views.edit_blog,name="edit_blog"),
path("delete/blogs/<str:slug>/",views.delete_blog,name="delete_blog"),
path("delete/image/blogs/<str:id>/",views.delete_blog_image,name="delete_blog_image"),
path("delete/videos/blogs/<str:id>/",views.delete_blog_video,name="delete_blog_video"),
path("get/video-length/<str:id>/",views.get_video_length,name="get_video_length"),
path("complete/blog/videos/<str:slug>/",views.add_video_blog,name="add_video_blog"),
path("check/blog/videos/<str:slug>/",views.check_blog_video,name="check_blog_video"),
path("complete/blog/audio/<str:slug>/",views.add_audio_blog,name="add_audio_blog"),
path("check/blog/audios/<str:slug>/",views.check_audio_blog,name="check_audio_blog"),


#### course
path("courses/",views.courses,name="courses"),
path("videos/",views.videos,name="videos"),
path("videos/<str:id>/",views.course_videos,name="course_videos"),

path("delete/videos/<str:slug>/",views.delete_videos,name="delete_videos"),

path("add/course/",views.add_course,name="add_course"),
path("add/video/<str:slug>/",views.add_video,name="add_video"),
path("upload/video/<str:slug>/",views.complete_add_video,name="complete_add_video"),
path("edit/courses/<str:slug>/",views.edit_course,name="edit_course"),
path("edit/video/<str:slug>/",views.edit_videos,name="edit_videos"),
path("delete/course_image/<str:id>/",views.edit_course_image,name="edit_course_image"),

#events
path("events/",views.events,name="events"),
path("demo/event/<int:id>/",views.demo_event,name="demo_event"),
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

#consultants
path("consultants/sessions/",views.consultants_sessions,name="consultants_sessions"),
path("consultants/activate/<int:id>/",views.accept_consultant,name="accept_consultant"),
path("consultants/start/<int:id>/",views.start_consultant,name="start_consultant"),
path("consultants/edit/<int:id>/",views.edit_consultant,name="edit_consultant"),
path("consultants/",views.consultants,name="consultants"),
path("consultants/add/category/",views.add_consultant_category,name="add_consultant_category"),

path("consultants/add/",views.add_consultant,name="add_consultant"),
path("consultants/complete/<str:id>/",views.complete_consultant,name="complete_consultant"),
path("consultants/delete/<str:id>/",views.delete_session,name="delete_session"),
path("consultants/sessions/activate/<str:id>/",views.active_session,name="active_session"),
####
###prices
path("prices/",views.prices,name="prices"),
path("price/edit/<str:id>/",views.edit_price,name="edit_price"),
path("price/add/",views.add_price,name="add_price"),

###
### terms
path("terms/",views.terms,name="terms"),
path("terms/add/",views.terms_add_new,name="terms_add_new"),
path("privacy/",views.privacy,name="privacy"),
path("privacy/add/",views.privacy_add_new,name="privacy_add_new"),
##
# Add user to course
path("user/course/add/",views.add_student_course,name="add_student_course"),
###
# Add user to director
path("user/director/add/",views.add_user_director,name="add_user_director"),
### add category 
path("category/add/",views.add_category,name="add_category"),
path("branch/add/",views.add_branch,name="add_branch"),
path("blog-category/add/",views.add_blog_category,name="add_blog_category"),

### emails
path("emails/",views.emails,name="emails"),
path("email/<int:id>/",views.single_email,name="single_email"),
path("close/email/<int:id>/",views.close_email,name="close_email"),

### certifications
path("certifications/",views.certifications,name="certifications"),
path("certification/approve/<int:id>/",views.edit_certifications,name="edit_certifications"),

### refunds
path("refunds/",views.refunds,name="refunds"),
path("refunds/search/",views.search_refunds,name="search_refunds"),
path("refunds/edit/<int:id>/",views.edit_refund,name="edit_refund"),
path("refunds/add/<int:id>/",views.add_refund,name="add_refund"),

#############
path("test/",views.test,name="test"),
path("check/videos/<str:slug>/",views.check_video,name="check_video"),




]  
