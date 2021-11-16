from django.db import models
from django.template.defaultfilters import slugify
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save
import string,random
from django.conf import settings
from django.shortcuts import render,redirect
from django.urls import reverse
User=settings.AUTH_USER_MODEL
def random_string_generator(size = 5, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
# Create your models here.

class Answers(models.Model):
    answer=models.TextField()
    question=models.ForeignKey("Question",related_name="question_answer",on_delete=models.CASCADE)
    correct=models.BooleanField(default=False)
    def __str__(self):
        return str(self.id)

class Question(models.Model):
    title=models.CharField(max_length=200)
    details=models.TextField(null=True,blank=True)
    answer=models.ManyToManyField(Answers,related_name="question_answer",blank=True)
    slug=models.SlugField(unique=True,blank=True,null=True)
    def __str__(self):
        return self.title



@receiver(pre_save, sender=Question)
def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug: 
        instance.slug = slugify(instance.title)
        if Question.objects.filter(slug=instance.slug).exists():
            slug=f"{instance.title}-{random_string_generator()}"
            instance.slug = slugify(slug)


class Quiz(models.Model):
    questions=models.ManyToManyField(Question)
    answers=models.ManyToManyField(Answers)
    course_id=models.PositiveIntegerField(default=0)
    def __str__(self):
        return (f"{self.id}") 
    
    def check_if_user_answer_question(self,student,question):
        student_answer= Student_Quiz.objects.filter(student=student,quiz=self,question=question)
        if student_answer.exists():
            answer=True
        else:
            answer=False 
        if self.get_student_answers_percent(student=student)["result"] == True:
            print("there")
            result=True
        else:
            
            result=False
        context={"result":result,"answer":answer}
        return context

    def get_student_answers_percent(self,student):
        student_answer= Student_Quiz.objects.filter(student=student,quiz=self).count()
        questions=self.questions.all().count()
        percent=(student_answer / questions ) * 100
        if percent == 100.0 :
            completed = True
        else:
            completed=False
        if student_answer == self.questions.count():
           result=True
        else:
            result=False
        context={"percent":percent,"completed":completed,"result":result}
        return context
    
    def next_quiz(self,question):
        my_quiz=self
        quiz_question=my_quiz.questions.get(id=int(question))
        qs=my_quiz.questions.all()
        for i in qs:
            if i.id > int(question):
                next=i.slug
                break
            else:
                next=False
        return next
    
    def previus_quiz(self,question):
        my_quiz=self
        quiz_question=my_quiz.questions.get(id=int(question))
        qs=my_quiz.questions.all().order_by("-id")
        for i in qs:
            # print(i)
            if i.id < int(question):
                prev=i.slug
                break
            #     next=i.slug
            #     break
            else:
                prev=False
        return prev
    def get_quiz_result(self,student):
        student=Student_Quiz.objects.filter(student=student,quiz=self)
        questions=self.questions.count()
        total=0
        flo="{0:.2f}"
        for i in student:
            if i.answer.correct == True:
                total +=1
        if total > 0:
            percent=flo.format((total/len(student)) *100)
            wrong_answer=student.count() - total
            right_answer=total
        else:
            right_answer=0
            percent=0
            wrong_answer=0
        context={"percent":percent,"answers":student.count(),"questions":questions,"right_answer":right_answer,
                 "wrong_answer":wrong_answer
                 }
        return context

class Student_Quiz(models.Model):
    student=models.ForeignKey(User,on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,on_delete=models.SET_NULL,null=True)
    question=models.ForeignKey(Question,on_delete=models.SET_NULL,null=True)
    answer=models.ForeignKey(Answers,on_delete=models.SET_NULL,null=True)


    def __str__(self): 
        return self.student.username

    def get_student_percent(self):
        student_quiz=Student_Quiz.objects.filter(student=self.student,quiz=self.quiz).count()
        quiz_questions=self.quiz.questions.all().count()
        percent=(student_quiz / quiz_questions) * 100
        flo="{0:.2f}"
        my_percent=flo.format(percent)
        if my_percent == 100.00:
            
            completed = True
        else:
            completed=False
        if student_quiz == quiz_questions :
            print("there")
            result=True
        else:
            result=False
        context={"percent":my_percent,"completed":completed,"result":result}
        return context