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
# Create your views here.

@login_required()
def quiz(request,course,question):
    my_course=get_object_or_404(Course,slug=course)
    if request.user in my_course.students.all():
        quiz=my_course.quiz
        quiz_question=quiz.questions.get(slug=question)
        answers=quiz_question.answer.all()
        user_progress=quiz.get_student_answers_percent(student=request.user)
        default_progress=quiz.check_if_user_answer_question(student=request.user,question=quiz_question)
        next=quiz.next_quiz(question=quiz_question.id)
        prev=quiz.previus_quiz(question=quiz_question.id)
        if request.is_ajax():
            answer=request.POST.get("answer")
            print(answer)
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
            # except:
            #     return FailedJsonResponse({"status":False})
    else:
        messages.error(request,"you should buy course first")
        return redirect(reverse("home:course",kwargs={"slug":my_course.slug}))
    context={"quiz":quiz,"course":my_course,"next":next,"prev":prev,"question":quiz_question,"answers":answers,"user_progress":user_progress,"default_progress":default_progress}
    return render(request,"quiz.html",context) 
    
@login_required()
def quiz_result(request,slug):
    course=get_object_or_404(Course,slug=slug)
    data=course.quiz.get_quiz_result(student=request.user)
    context={"course":course,"data":data}
    return render(request,"result.html",context)
