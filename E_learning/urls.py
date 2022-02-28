"""E_learning URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from . import views
from django.urls import path,include,re_path
from django.conf.urls import (handler400, handler403, handler404, handler500
)
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
import os 
# import debug_toolbar
# from allauth.urls


# urlpatterns = [
# ]
urlpatterns = i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('agartha/admin/dashboard/', admin.site.urls),
    # path('oauth/', include('social_django.urls', namespace='social')), 
    path('accounts/', include('allauth.urls')),    
    path('', include("home.urls",namespace="home")),
    path('quiz/', include("Quiz.urls",namespace="quiz")), 
    path('profile/', include("accounts.urls",namespace="accounts")),
    path('ckeditor/', include('ckeditor_uploader.urls')),  
    # url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], protected_serve, {'document_root': settings.MEDIA_ROOT}),
    path('blogs/', include('Blogs.urls',namespace="blogs")),  
    path('consultant/', include('Consultant.urls',namespace="consultant")),  
    path('dashboard/', include('Dashboard.urls',namespace="dashboard")),  
    path("language/",views.change_language,name="language"), 
    # path('__debug__/', include(debug_toolbar.urls)),
    re_path('rosetta/', include('rosetta.urls')),prefix_default_language=False,
 
)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


handler404 = 'home.views.my_custom_page_not_found_view'
handler500 = 'home.views.my_custom_error_view'
handler403 = 'home.views.my_custom_permission_denied_view'
handler400 = 'home.views.my_custom_bad_request_view'   