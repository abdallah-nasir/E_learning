# Generated by Django 3.2.8 on 2022-03-10 21:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0006_delete_test'),
        ('home', '0006_auto_20220214_1451'),
        ('library', '0004_auto_20220310_1411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='library_videos',
            name='videos_ptr',
        ),
        migrations.DeleteModel(
            name='Library_Course',
        ),
        migrations.DeleteModel(
            name='Library_Videos',
        ),
    ]
