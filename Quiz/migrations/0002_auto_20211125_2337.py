# Generated by Django 3.2.8 on 2021-11-25 21:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student_quiz',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Quiz.question'),
        ),
        migrations.AlterField(
            model_name='student_quiz',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Quiz.quiz'),
        ),
    ]
