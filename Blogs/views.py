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
    paginator = Paginator(blogs, 8) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"blogs":page_obj}
    return render(request,"blogs.html",context)

# def single_blog(request,slug):
#     categories=Category.objects.all()
#     blog=get_object_or_404(Blog,slug=slug)
#     if request.user.is_authenticated:
#         user=request.user
#         try:
#             viewers=blog.blog_viewers.viewers.all()
#             if user in viewers:
#                 pass
#             else:
#                 blog.blog_viewers.viewers.add(request.user)
#                 blog.blog_viewers.save()
#         except:
#             pass

#     context={"blog":blog,"categories":categories,"popular":popular_blogs()}
#     return render(request,"blog-singel.html",context)

# def blog_search(request):
#     categories=Category.objects.all()
#     qs=request.GET.get("qs")
#     blog=Blog.objects.filter(Q(name__icontains=qs) | Q(details__icontains=qs) | Q(category__name__icontains=qs)).distinct() 
#     if len(blog) == 0:
#         qs=None
#         page_obj=[]
#     else:
#         paginator = Paginator(blog, 8) # Show 25 contacts per page.
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#     return render(request,"blog_search.html",{"blog":page_obj,"qs":qs,"categories":categories,"popular":popular_blogs()})




# def blog_comment(request):
#     try:
#         id=request.POST.get("blog_id")
#         blog=Blog.objects.get(id=id)
#         if request.user.is_authenticated:
#             comment=request.POST.get("comment")
#             if comment:
#                 print("comment here")
#                 comment= Blog_Comment.objects.create(blog_id=id,comment=comment,user=request.user)
#                 blog.comments.add(comment)
#                 blog.save()
#                 return redirect(reverse("home:blog",kwargs={"slug":blog.slug}))
#                 # return JsonResponse({"comment":comment.comment,"image":comment.user.image.url,"first_name":comment.user.first_name.title(),"last_name":comment.user.last_name.title(),"created":time_string})

#             else: 
#                 messages.error(request,"you cant submit blank comment")
#                 return redirect(reverse("home:blog",kwargs={"slug":blog.slug}))

#         else:
#             messages.error(request,"login first")
#             return redirect(reverse("home:blog",kwargs={"slug":blog.slug}))
#     except:
#         print("as")
#         return redirect(reverse("home:blogs"))
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