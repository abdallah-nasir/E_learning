# Generated by Django 3.2.8 on 2021-11-30 12:00

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('Blogs', '0013_alter_blog_managers'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='blog',
            managers=[
                ('check_reject', django.db.models.manager.Manager()),
            ],
        ),
    ]
