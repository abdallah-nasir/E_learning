# Generated by Django 3.2.8 on 2022-02-02 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
