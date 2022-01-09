from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from .models import TeacherForms
from django.contrib import messages
from django.contrib.auth import get_user_model
User=get_user_model()


def check_user_is_student(function):
    def wrap(request, *args, **kwargs):
        if request.user.account_type == "teacher":
            messages.error(request,"you are already a teacher")
            return redirect(reverse("accounts:account_info"))
        elif request.user.account_type == 'student':
            form=TeacherForms.objects.filter(teacher=request.user)
            if form.exists():
                if form[0].status == "pending":
                    messages.error(request,"your request is being review by admins")
                    return redirect(reverse("accounts:account_info"))
                elif form[0].status == 'approved':
                    messages.success(request,"your request has been approved")
                    return redirect(reverse("dashboard:home"))
                else:
                    return function(request, *args, **kwargs)

            else:
                return function(request, *args, **kwargs)

        else:
            return redirect(reverse("accounts:account_info"))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap