from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from Frontend.models import *
from .decorators import admin_director_check
from django.contrib.auth.decorators import login_required
from .forms import AddFaq , AddBranchFaq , AddCategoryFaq
from django.core.paginator import Paginator


@login_required(login_url="accounts:login")
@admin_director_check
def add_category(request):
    form=AddCategoryFaq(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            form.save()
            messages.success(request,"category added successfully")
    context={"form":form}
    return render(request,"faqs/dashboard_add_category.html",context)


@login_required(login_url="accounts:login")
@admin_director_check
def add_branch(request):
    form=AddBranchFaq(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance=form.save(commit=False)
            form.save()
            messages.success(request,"Branch added successfully")
    context={"form":form}
    return render(request,"faqs/dashboard_add_branch.html",context)
import json

@login_required(login_url="accounts:login")
@admin_director_check
def add_faqs(request):
    form=AddFaq(request.POST or None,request.FILES or None)
    if request.is_ajax():
        category = request.POST.get("category")
        if category:
            branches = Branch.objects.filter(category_id=int(category))
            return JsonResponse(list(branches.values()),safe=False)
        else:   
            return JsonResponse(list(),safe=False)
    if request.method == "POST":
        branch = Branch.objects.filter(category__id=int(request.POST.get("category")))
        form.fields["branch"].queryset = branch
        if form.is_valid(): 
            instance=form.save(commit=False)
            form.save()
            messages.success(request,"Faq added successfully")
    context={"form":form}
    return render(request,"faqs/dashboard_add_faqs.html",context)


@login_required(login_url="accounts:login")
@admin_director_check
def all_category(request):
    category = Category.objects.all()
    context={"category":category}
    return render(request,"faqs/dashboard_all_category.html",context)
    
@login_required(login_url="accounts:login")
@admin_director_check
def all_branch(request):
    branch = Branch.objects.all()
    context={"branch":branch}
    return render(request,"faqs/dashboard_all_branch.html",context)
    
@login_required(login_url="accounts:login")
@admin_director_check
def faqs(request):
    faqs = Faq.objects.all()
    paginator = Paginator(faqs, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"faqs":page_obj}
    return render(request,"faqs/dashboard_all_faqs.html",context)
    
@login_required(login_url="accounts:login")
@admin_director_check
def edit_faq(request,id):
    faq=get_object_or_404(Faq,id=id)
    form=AddFaq(request.POST or None,instance=faq)
    if request.is_ajax():
        category = request.POST.get("category")
        if category:
            branches = Branch.objects.filter(category_id=int(category))
            return JsonResponse(list(branches.values()),safe=False)
        else:   
            return JsonResponse(list(),safe=False)
    if request.method == "POST":
        branch = Branch.objects.filter(category__id=int(request.POST.get("category")))
        form.fields["branch"].queryset = branch
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save() 
            messages.success(request,"Faq Edited successfully")
            return redirect(reverse("dashboard:faqs:faqs"))
    context={"form":form,"faq":faq}  
    return render(request,"faqs/dashboard_edit_faqs.html",context)

    
@login_required(login_url="accounts:login")
@admin_director_check
def delete_faq(request,id):
    faq=get_object_or_404(Faq,id=id)
    faq.delete()
    messages.success(request,"Faq deleted successfully")
    return redirect(reverse("dashboard:faqs:faqs"))