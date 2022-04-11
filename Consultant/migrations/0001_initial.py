# Generated by Django 3.2.8 on 2022-04-06 17:32

import Consultant.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Consultant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(auto_now_add=True)),
                ('end_time', models.TimeField(auto_now_add=True)),
                ('date', models.DateField(null=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('started', 'started'), ('completed', 'completed'), ('refund', 'refund')], default='pending', max_length=50)),
                ('zoom', models.TextField(blank=True)),
                ('user_data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Cosultant_Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('bank', 'bank'), ('Western Union', 'Western Union'), ('Paypal', 'Paypal')], max_length=50)),
                ('payment_image', models.ImageField(null=True, upload_to=Consultant.models.upload_consultant_payment)),
                ('transaction_number', models.CharField(max_length=50, null=True)),
                ('amount', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=50)),
                ('user_data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Teacher_Time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.IntegerField(choices=[(6, 'Saturday'), (7, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday')], default=1)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('price', models.FloatField(default=0)),
                ('available', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserDataForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('date', models.DateField(null=True)),
                ('accomplished', models.BooleanField(default=False)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Consultant.teacher_time')),
            ],
        ),
    ]
