# Generated by Django 3.2.8 on 2022-01-09 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Frontend', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='terms',
            old_name='text_a',
            new_name='text_ar',
        ),
        migrations.RemoveField(
            model_name='terms',
            name='text_r',
        ),
    ]
