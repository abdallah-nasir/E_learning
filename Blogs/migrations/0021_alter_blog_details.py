# Generated by Django 3.2.8 on 2021-12-27 16:56

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Blogs', '0020_auto_20211210_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='details',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
