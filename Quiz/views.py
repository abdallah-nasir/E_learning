from django.shortcuts import render,redirect
from django.urls import reverse
from .models import *
from home.models import Course
from home.views import FailedJsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import check_course_status,check_if_payment_has_expired
from django.core.mail import EmailMessage,get_connection
import os
PAYMENT_EMAIL_USERNAME = os.environ['PAYMENT_EMAIL_USERNAME']
PAYMENT_EMAIL_PASSWORD = os.environ['PAYMENT_EMAIL_PASSWORD']
PAYMENT_EMAIL_PORT = os.environ['PAYMENT_EMAIL_PORT']
SUPPORT_EMAIL_HOST = os.environ['SUPPORT_EMAIL_HOST']
PAYMENT_MAIL_CONNECTION = get_connection(
host= SUPPORT_EMAIL_HOST, 
port=PAYMENT_EMAIL_PORT, 
username=PAYMENT_EMAIL_USERNAME, 
password=PAYMENT_EMAIL_PASSWORD, 
use_tls=False
) 
TASK_NOTIFICATION_EMAIL_USERNAME=os.environ['TASK_NOTIFICATION_EMAIL_USERNAME']
TASK_NOTIFICATION_EMAIL_PASSWORD=os.environ['TASK_NOTIFICATION_EMAIL_PASSWORD']
TASK_NOTIFICATION_EMAIL_HOST=os.environ["TASK_NOTIFICATION_EMAIL_HOST"]
TASK_NOTIFICATION_EMAIL_PORT=os.environ["TASK_NOTIFICATION_EMAIL_PORT"]
TASK_NOTIFICATION_EMAIL_CONNECTION=get_connection(
host= TASK_NOTIFICATION_EMAIL_HOST, 
port=TASK_NOTIFICATION_EMAIL_PORT, 
username=TASK_NOTIFICATION_EMAIL_USERNAME, 
password=TASK_NOTIFICATION_EMAIL_PASSWORD, 
use_tls=False
)
def send_mail_approve(request,user,body,subject):
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=TASK_NOTIFICATION_EMAIL_USERNAME,
        to=[TASK_NOTIFICATION_EMAIL_USERNAME],
        reply_to=[user],
        connection=TASK_NOTIFICATION_EMAIL_CONNECTION
        )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    return True
# Create your views here.

@login_required(login_url="accounts:login")
@check_course_status
@check_if_payment_has_expired
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
@check_if_payment_has_expired
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
            msg = EmailMessage(
            subject="Quiz Completed", 
            body="thank you for your answers,our team will send you mail for the certification", 
            from_email=PAYMENT_EMAIL_USERNAME,
            to=[result.user.email],
            connection=PAYMENT_MAIL_CONNECTION
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            result.status ="completed"
            result.save()
            Certification.objects.create(user=request.user,result=result)       #quiz may have more cerifications due to questions changes
            body=f"new certification for user {request.user.email}"
            subject="new certification"
            send_mail_approve(request,body=body,subject=subject,user=request.user.email)
            messages.success(request,f"we have sent Email to {result.user.email},Please check it")
    context={"course":course,"data":data}
    return render(request,"result.html",context)
