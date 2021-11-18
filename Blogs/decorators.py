from django.core.exceptions import PermissionDenied
from .models import Blog
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Blog_Payment
def check_user_is_member(function):
    def wrap(request, *args, **kwargs):

        blog = Blog.objects.get(slug=kwargs['slug'])
        if blog.paid == True:
            if request.user.vip == True:
                return function(request, *args, **kwargs)
            else:
                messages.error(request,"You Should Be A Member To Access Blogs")
                return redirect(reverse("blogs:blogs"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



def check_user_status(function):
    def wrap(request, *args, **kwargs):
        if request.user.vip == True or Blog_Payment.objects.filter(user=request.user,pending=True).exists():
            messages.error(request,"You Already A Member")
            return redirect(reverse("blogs:blogs"))
        elif Blog_Payment.objects.filter(user=request.user,pending=True).exists():
            messages.error(request,"our team will review your request")
            return redirect(reverse("blogs:blogs"))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap