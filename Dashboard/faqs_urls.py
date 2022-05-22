from django.urls import path,include
from . import faqs as views
app_name="Dashboard"
  
urlpatterns = [
# path("category/",views.all_category,name="all_category"),
# path("branch/",views.all_branch,name="all_branch"),
path("faqs/",views.faqs,name="faqs"),

path("add/category/",views.add_category,name="add_category"),
path("add/branch/",views.add_branch,name="add_branch"),
path("add/faqs/",views.add_faqs,name="add_faqs"),
path("edit/faq/<int:id>/",views.edit_faq,name="edit_faq"),
path("delete/faq/<int:id>/",views.delete_faq,name="delete_faq"),

]  
