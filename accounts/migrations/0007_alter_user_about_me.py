# Generated by Django 3.2.4 on 2021-10-15 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_user_about_me'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='about_me',
            field=models.TextField(blank=True, null=True),
        ),
    ]
