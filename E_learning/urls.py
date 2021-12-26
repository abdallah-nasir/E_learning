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
from django.http.response import FileResponse
from django.shortcuts import render,get_object_or_404
from django.urls import path,include,re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
import os 
from . import views
# import debug_toolbar
# from allauth.urls


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),    
    path('', include("home.urls",namespace="home")),
    path('quiz/', include("Quiz.urls",namespace="quiz")), 
    path('profile/', include("accounts.urls",namespace="accounts")),
    path('ckeditor/', include('ckeditor_uploader.urls')),  
    # url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], protected_serve, {'document_root': settings.MEDIA_ROOT}),
    path('blogs/', include('Blogs.urls',namespace="blogs")),  
    path('consultant/', include('Consultant.urls',namespace="consultant")),  
    path('dashboard/', include('Dashboard.urls',namespace="dashboard")),  
    # path('__debug__/', include(debug_toolbar.urls)),

    re_path('rosetta/', include('rosetta.urls')),prefix_default_language=False)
       
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
