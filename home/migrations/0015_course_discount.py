# Generated by Django 3.2.8 on 2021-12-01 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_alter_payment_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='discount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]