from django.contrib import admin
from . import views
from django.urls import path,include,re_path
from django.conf.urls import (handler400, handler403, handler404, handler500
)
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
import os 

urlpatterns = i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('agartha/admin/dashboard/', admin.site.urls),
    path('accounts/', include('allauth.urls')),    
    path('', include("home.kemet_urls",namespace="home")),
    path('quiz/', include("Quiz.kemet_urls",namespace="quiz")), 
    path('profile/', include("accounts.kemet_urls",namespace="accounts")),
    path('ckeditor/', include('ckeditor_uploader.urls')),  
    path('blogs/', include('Blogs.kemet_urls',namespace="blogs")),  
    path('consultant/', include('Consultant.kemet_urls',namespace="consultant")),  
    path('library/', include('library.kemet_urls',namespace="library")),  
    path('dashboard/', include('Dashboard.urls',namespace="dashboard")),  
    path("language/",views.change_language,name="language"), 
    # path('__debug__/', include(debug_toolbar.urls)),
    re_path('rosetta/', include('rosetta.urls')),prefix_default_language=False,   
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    
handler404 = 'home.kemet_views.my_custom_page_not_found_view'
handler500 = 'home.kemet_views.my_custom_error_view'
handler403 = 'home.kemet_views.my_custom_permission_denied_view'
handler400 = 'home.kemet_views.my_custom_bad_request_view'   