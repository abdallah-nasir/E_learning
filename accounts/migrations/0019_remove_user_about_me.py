# Generated by Django 3.2.8 on 2021-11-17 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_teacherforms'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='about_me',
        ),
    ]
