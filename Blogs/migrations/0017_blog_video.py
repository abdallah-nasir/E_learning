# Generated by Django 3.2.8 on 2021-12-01 10:50

import Blogs.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blogs', '0016_alter_blog_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to=Blogs.models.upload_blog_videos),
        ),
    ]
