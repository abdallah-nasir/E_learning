# Generated by Django 3.2.8 on 2022-01-23 13:31

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20220122_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='date',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date.today)]),
        ),
    ]
