# Generated by Django 3.2.8 on 2021-12-21 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Consultant', '0015_alter_teacher_time_date'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='cosultant_payment',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='teacher_time',
            name='available',
            field=models.BooleanField(default=True),
        ),
    ]
