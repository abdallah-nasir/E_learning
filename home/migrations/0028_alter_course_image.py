# Generated by Django 3.2.8 on 2021-12-16 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_videos_video_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.URLField(),
        ),
    ]
