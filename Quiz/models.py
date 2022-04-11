from django.db import models
from django.template.defaultfilters import slugify
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save
import string,random
from django.conf import settings
from django.shortcuts import render,redirect
from django.urls import reverse
from home import models as home_models

User=settings.AUTH_USER_MODEL
def random_string_generator(size = 5, chars = string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
# Create your models here.
def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str
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
    slug=models.SlugField(unique=True)
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        print(self.slug)

        if not self.slug:
            self.slug = slugify(self.title)
            if Question.objects.filter(slug=self.slug).exists():
                slug=slugify(self.title)
                self.slug =f"{slug}-{random_string_generator()}"
            else:
                self.slug = slugify(self.title)    
                print("ehre")

        super(Question, self).save()


   

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
            result=True
        else:
            
            result=False
        context={"result":result,"answer":answer}
        return context
   
    def change_result_status(self,student):
        try:
            result=Quiz_Result.objects.get(user=student,quiz=self)
            if result.status == 'completed':
                result.status ="in-completed"
                result.save()
                completed = False
            else:
                completed = True
        except:
            completed=True 
        return completed
    def get_student_answers_percent(self,student):
        student_answer= Student_Quiz.objects.filter(student=student,quiz=self).count()
        questions=self.questions.all().count()
        percent=(student_answer / questions ) * 100
        if percent == 100.0 :
            completed = True
        else:
            completed=False
            change_result=self.change_result_status(student)
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
        if len(student) == questions:
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
                wrong_answer=student.count()
            context={"allowed":True,"percent":percent,"answers":student.count(),"questions":questions,"right_answer":right_answer,
                    "wrong_answer":wrong_answer
                    }
        else:

            context={"allowed":False}
        return context

class Student_Quiz(models.Model):
    student=models.ForeignKey(User,on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
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
QUIZ_STATUS=(
    ("completed","completed"),
    ("in-completed","in-completed"),
)

CERTI_STATUS=(
    ("received","received"),
    ("pending","pending"),
)
class Quiz_Result(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,null=True,on_delete=models.SET_NULL)
    degree=models.FloatField(default=0)
    status=models.CharField(choices=QUIZ_STATUS,max_length=50,default="in-completed")
    certification=models.CharField(choices=CERTI_STATUS,max_length=50,default="pending")
    def __str__(self):
        return str(self.id)

class Certification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    result=models.ForeignKey(Quiz_Result,related_name="quiz_certification",on_delete=models.SET_NULL,null=True)
    image=models.ImageField(null=True)
    status=models.CharField(max_length=50,choices=CERTI_STATUS,default="pending")
    date_created=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def get_certification_course(self):
        try:
            course_id=self.result.quiz.course_id
            quiz_course=home_models.Course.objects.get(id=course_id)
            course=quiz_course.name
        except:
            course=None
        return course
