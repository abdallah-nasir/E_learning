# Generated by Django 3.2.8 on 2021-11-11 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0006_alter_question_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='answers',
            field=models.ManyToManyField(to='Quiz.Answers'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='course_id',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
