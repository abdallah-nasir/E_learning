# Generated by Django 3.2.8 on 2021-11-21 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_videos_video'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='ordered',
            new_name='pending',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='phone',
        ),
    ]
