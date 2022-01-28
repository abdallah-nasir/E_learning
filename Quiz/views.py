from django.shortcuts import render,redirect
from django.urls import reverse
from .models import *
from home.models import Course
from home.views import FailedJsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from next_prev import next_in_order, prev_in_order
from django.contrib import messages
from .decorators import check_course_status
from django.core.mail import send_mail,EmailMessage

# Create your views here.

@login_required(login_url="accounts:login")
@check_course_status
def quiz(request,slug,question):
    my_course=get_object_or_404(Course,slug=slug,status="approved")
    
    try:
        quiz_question=my_course.quiz.questions.get(slug=question)  
    except:
        messages.error(request,"invalid question")
        return redirect(reverse("home:course",kwargs={"slug":slug}))
    quiz=my_course.quiz
    answers=quiz_question.answer.all()
    user_progress=quiz.get_student_answers_percent(student=request.user)
    default_progress=quiz.check_if_user_answer_question(student=request.user,question=quiz_question)
    next=quiz.next_quiz(question=quiz_question.id)
    prev=quiz.previus_quiz(question=quiz_question.id)
    if request.is_ajax():
        answer=request.POST.get("answer")
        # try:
        quiz_answer=quiz_question.answer.get(id=int(answer))
        student_quiz,created=Student_Quiz.objects.get_or_create(student=request.user,
        quiz=quiz,question=quiz_question)
        if student_quiz.answer:
            return FailedJsonResponse({"status":False})
        else:
            student_quiz.answer = quiz_answer
            student_quiz.save()
            if quiz_answer.correct == True:
                message=True
            else:
                message=False
            return JsonResponse({"percent":student_quiz.get_student_percent(),"message":message})

    context={"quiz":quiz,"course":my_course,"next":next,"prev":prev,"question":quiz_question,"answers":answers,"user_progress":user_progress,"default_progress":default_progress}
    return render(request,"quiz.html",context) 
     
@login_required(login_url="accounts:login")   
@check_course_status
def quiz_result(request,slug):
    course=get_object_or_404(Course,slug=slug)
    data=course.quiz.get_quiz_result(student=request.user)
    if data["allowed"] == False:
        messages.error(request,"You didn't complete Quiz Yet")
        return redirect(reverse("home:course",kwargs={"slug":course.slug}))
    else:
        result,created=Quiz_Result.objects.get_or_create(user=request.user,quiz=course.quiz)
        result.degree=data["percent"]
        result.save()
        if created or result.status == "in-completed":
            msg = EmailMessage(subject="Quiz Completed", body="thank you for your answers,our team will send you mail for the certification", 
            from_email=settings.EMAIL_HOST_USER, to=[result.user.email])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            result.status ="completed"
            result.save()
            Certification.objects.create(user=request.user,result=result)       #quiz may have more cerifications due to questions changes
            messages.success(request,f"we have sent Email to {result.user.email},Please check it")
    context={"course":course,"data":data}
    return render(request,"result.html",context)
