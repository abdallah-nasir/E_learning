from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import Group
def check_user_validation(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_director:
            return function(request, *args, **kwargs)
        elif request.user.account_type == 'teacher' and request.user.is_active == True:
            return function(request, *args, **kwargs)
        else:
            messages.error(request,"You Don't Have Permission To Login to DashBoard")
            return redirect(reverse("home:home"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
