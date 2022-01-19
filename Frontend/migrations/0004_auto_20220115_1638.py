# Generated by Django 3.2.8 on 2022-01-15 16:38

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Frontend', '0003_terms_text_en'),
    ]

    operations = [
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', ckeditor.fields.RichTextField()),
                ('text_en', ckeditor.fields.RichTextField(null=True)),
                ('text_ar', ckeditor.fields.RichTextField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='terms',
            name='text',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='terms',
            name='text_ar',
            field=ckeditor.fields.RichTextField(null=True),
        ),
        migrations.AlterField(
            model_name='terms',
            name='text_en',
            field=ckeditor.fields.RichTextField(null=True),
        ),
    ]
