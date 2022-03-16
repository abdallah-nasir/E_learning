# Generated by Django 3.2.8 on 2022-03-13 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_course_domain_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='domain_type',
            field=models.IntegerField(choices=[(1, 'agartha'), (2, 'kemet')], default=1),
        ),
    ]
