# Generated by Django 3.2 on 2022-04-18 15:27

from django.db import migrations, models
import library.models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0009_rename_test_file_e_book_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='e_book',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to=library.models.pdf_upload),
        ),
    ]
