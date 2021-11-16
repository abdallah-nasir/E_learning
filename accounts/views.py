from django.shortcuts import render,redirect,reverse
from django.contrib.auth import logout 
from django.contrib import messages
from .forms import Teacher_Form 
from .models import TeacherForms
from .models import User
# Create your views here.


def logout_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse("home:home"))
    else:
        logout(request)
        messages.success(request,"you have logged out")
        return redirect(reverse("home:home"))

def check_teacher_form(request):
    form=Teacher_Form(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                teacher_username=form.cleaned_data["username"]
                user=User.objects.get(username=teacher_username)
                teacher_form=TeacherForms.objects.filter(teacher__username=teacher_username,approved=False)
                if teacher_form.exists():
                    messages.error(request,"your already have a Form")
                    form=Teacher_Form()
                else: 
                    facebook=form.cleaned_data['facebook']
                    linkedin=form.cleaned_data['linkedin']
                    twitter=form.cleaned_data['twitter']
                    about_me=form.cleaned_data['about_me']
                    title=form.cleaned_data['title']
                    code=form.cleaned_data['code']
                    data=[{"social":{"facebook":facebook,"linkedin":linkedin,"twitter":twitter},
                        "about_me":about_me,"title":title}]
                    TeacherForms.objects.create(teacher=user,data=data,code=code,approved=False)
                    messages.success(request,"your request is being review by admins")
                    form=Teacher_Form()
            except:
                messages.error(request,"invalid data")
                form=Teacher_Form()
    context={"form":form}
    return render(request,"check_teacher.html",context)