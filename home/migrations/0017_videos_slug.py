# Generated by Django 3.2.8 on 2021-10-18 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_course_students'),
    ]

    operations = [
        migrations.AddField(
            model_name='videos',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
