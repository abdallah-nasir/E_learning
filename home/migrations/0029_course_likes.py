# Generated by Django 3.2.8 on 2021-10-24 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_wishlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
