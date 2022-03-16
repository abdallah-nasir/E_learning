from .models import *
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404

def check_if_in_library(function):
    def wrap(request, *args, **kwargs):
        library=get_object_or_404(Library,slug=kwargs["slug"])
        if library.paid:
            if library.students.filter(username=request.user.username):
                return function(request, *args, **kwargs)
            else:
                messages.error(request,"You Should Buy This Content First")
                return redirect(reverse("accounts:account_info"))
        else:
            if request.user.vip:
                return function(request, *args, **kwargs)
            else:
                messages.error(request,"You Should Be Member")
                return redirect(reverse("blogs:pricing"))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

