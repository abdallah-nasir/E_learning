# Generated by Django 3.2.8 on 2022-04-09 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='library_payment',
            name='expired',
            field=models.BooleanField(default=False),
        ),
    ]