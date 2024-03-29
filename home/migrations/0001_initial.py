# Generated by Django 3.2.8 on 2022-04-06 17:32

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import home.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Quiz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('domain_type', models.IntegerField(choices=[(1, 'agartha'), (2, 'kemet')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('image', models.ImageField(upload_to='')),
                ('domain_type', models.IntegerField(choices=[(1, 'agartha'), (2, 'kemet')], default=1)),
                ('duration', models.FloatField(default=0)),
                ('price', models.FloatField(default=0)),
                ('discount', models.PositiveIntegerField(default=0)),
                ('course_status', models.CharField(choices=[('on process', 'on process'), ('complete', 'complete')], max_length=50)),
                ('details', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined')], default='pending', max_length=50)),
                ('stars', models.FloatField(default=0)),
                ('likes', models.PositiveIntegerField(default=0)),
                ('collection', models.CharField(default='#', max_length=200)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('Instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instractor', to=settings.AUTH_USER_MODEL)),
                ('branch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.branch')),
                ('quiz', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Quiz.quiz')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('name_en', models.CharField(max_length=200, null=True)),
                ('name_ar', models.CharField(max_length=200, null=True)),
                ('link', models.CharField(blank=True, default='#', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ManyToManyField(blank=True, to='home.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Videos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('video', models.FileField(upload_to='')),
                ('video_uid', models.CharField(default='0', max_length=200)),
                ('details', models.TextField()),
                ('duration', models.FloatField(default=0)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('my_course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course', to='home.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('watched_users', models.ManyToManyField(blank=True, related_name='watched_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Testimonials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher_review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField(blank=True, null=True)),
                ('rate', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_review', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_review', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Support_Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=100)),
                ('subject', models.CharField(max_length=80)),
                ('phone', models.CharField(max_length=20)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'pending'), ('solved', 'solved'), ('on process', 'on process')], default='pending', max_length=20)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=100)),
                ('phone', models.CharField(max_length=25)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField(blank=True, null=True)),
                ('rate', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_course', to='home.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('bank', 'bank'), ('Western Union', 'Western Union'), ('Paypal', 'Paypal')], max_length=50)),
                ('payment_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('transaction_number', models.CharField(max_length=50, null=True)),
                ('amount', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=50)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('expired_at', models.DateField(auto_now_add=True)),
                ('expired', models.BooleanField(default=False)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.course')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('details', models.TextField()),
                ('image', models.ImageField(upload_to=home.models.upload_events_images)),
                ('date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date.today)])),
                ('status', models.CharField(choices=[('approved', 'approved'), ('declined', 'declined'), ('pending', 'pending'), ('start', 'start'), ('completed', 'completed')], default='pending', max_length=20)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('place', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.branch')),
                ('students', models.ManyToManyField(blank=True, related_name='event_students', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='reviews',
            field=models.ManyToManyField(blank=True, related_name='course_reviews', to='home.Reviews'),
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='videos',
            field=models.ManyToManyField(to='home.Videos'),
        ),
        migrations.AddField(
            model_name='branch',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.category'),
        ),
    ]
