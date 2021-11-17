from django.shortcuts import render

# Create your views here.
from django.db.models.query_utils import Q
from django.shortcuts import render,redirect,reverse
from .models import *
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .forms import *
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse,HttpResponseRedirect
from django.db.models import Q
from itertools import chain
from django.conf import settings
from accounts.models import User
from django.core.mail import send_mail,EmailMessage
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from datetime import datetime
from django.forms import ValidationError




def home(request):
    blogs=Blog.objects.filter(approved=True)
    paginator = Paginator(blogs, 9) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj,"slider":blog_slider()}
    return render(request,"blogs.html",context)

@login_required()
def single_blog(request,slug):
    blog=get_object_or_404(Blog,slug=slug)
    comment_form=CommentForm(request.POST or None)
    viewers=blog.check_blog_viwers(request.user)
    categories=recent_categories()
    context={"blog":blog,"categories":categories,"comment_form":comment_form}
    return render(request,"blog.html",context)

def blog_search(request):
    qs=request.GET.get("search")
    blog=Blog.objects.filter(Q(name__icontains=qs,approved=True) | Q(details__icontains=qs,approved=True) | Q(category__name__icontains=qs,approved=True) |Q(tags__name__icontains=qs,approved=True)).distinct() 
    print(blog)
    if len(blog) == 0:
        qs=None
        page_obj=[]
    else:
        paginator = Paginator(blog, 9) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,"blog_search.html",{"blogs":page_obj,"qs":qs})

def blog_comment(request,id):
    if request.user.is_authenticated:
        form=CommentForm(request.POST)
        blog=get_object_or_404(Blog,id=id)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.user=request.user
            instance.blog=blog
            instance.save()
            instance.blog.comments.add(instance)
            instance.blog.save()
            form=CommentForm()
    else:
        messages.error(request,"You Should Sign in First")
    return redirect(reverse("blogs:blog",kwargs={"slug":instance.blog.slug}))


def blog_comment_reply(request,id,reply):
    if request.user.is_authenticated:
        form=ReplyForm(request.POST)
        blog=get_object_or_404(Blog,id=id)
        try:
            comment=blog.comments.get(id=reply)
        except:
            return redirect(reverse("blogs:blog",kwargs={"slug":blog.slug}))
        if form.is_valid():
            instance=form.save(commit=False)
            instance.user=request.user
            instance.blog=blog
            instance.comment=comment
            instance.save()
            form=CommentForm()
    else:
        messages.error(request,"You Should Sign in First")
    return redirect(reverse("blogs:blog",kwargs={"slug":instance.blog.slug}))
# def blog_comment_reply(request):
#     # try:
#     comment_id=request.POST.get("comment_id")
#     blog_id=request.POST.get("blog_id")
#     reply=request.POST.get("reply")
#     blog=Blog.objects.get(id=blog_id)
#     if request.user.is_authenticated:  
#         if reply:
#             print("comment here")
#             reply= Blog_Comment_Reply.objects.create(blog=blog,comment_id=comment_id,reply=reply,user=request.user)
#             return redirect(reverse("home:blog",kwargs={"slug":blog.slug}))
#             # return JsonResponse({"comment":comment.comment,"image":comment.user.image.url,"first_name":comment.user.first_name.title(),"last_name":comment.user.last_name.title(),"created":time_string})
#         else: 
#             messages.error(request,"you cant submit blank reply")
#             return redirect(reverse("home:blog",kwargs={"slug":blog.slug}))

#     else:
#         messages.error(request,"login first")
#         return redirect(reverse("home:blog",kwargs={"slug":blog.slug}))
#     # except:
#     #     print("as")
#     #     return redirect(reverse("home:blogs"))