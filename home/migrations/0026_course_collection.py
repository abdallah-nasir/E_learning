# Generated by Django 3.2.8 on 2021-12-14 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0025_rename_video_videos_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='collection',
            field=models.CharField(default='#', max_length=200),
        ),
    ]