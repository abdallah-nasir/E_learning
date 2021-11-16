# Generated by Django 3.2.8 on 2021-11-12 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0009_student_quiz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='answer',
        ),
        migrations.AddField(
            model_name='question',
            name='answer',
            field=models.ManyToManyField(blank=True, related_name='question_answer', to='Quiz.Answers'),
        ),
    ]
