# Generated by Django 3.2.8 on 2022-01-22 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_rename_suppot_email_support_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='name_ar',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='name_en',
            field=models.CharField(max_length=200, null=True),
        ),
    ]