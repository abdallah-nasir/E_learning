# Generated by Django 3.2.8 on 2022-01-11 06:05

from django.db import migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Consultant', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher_time',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(default=1),
            preserve_default=False,
        ),
    ]