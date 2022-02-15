# Generated by Django 3.2.8 on 2022-02-08 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0003_auto_20220203_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refunds',
            name='type',
            field=models.CharField(choices=[('course_payment', 'course_payment'), ('consultant_payment', 'consultant_payment'), ('blog_payment', 'blog_payment')], max_length=50),
        ),
    ]