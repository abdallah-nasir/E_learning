# Generated by Django 3.2.8 on 2022-04-06 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddStudentCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Ads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_type', models.IntegerField(choices=[(1, 'agartha'), (2, 'kemet')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Refunds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('course_payment', 'course_payment'), ('consultant_payment', 'consultant_payment'), ('blog_payment', 'blog_payment'), ('movie_payment', 'movie_payment'), ('music_payment', 'music_payment'), ('audio_book_payment', 'audio_book_payment')], max_length=50)),
                ('content_id', models.PositiveIntegerField(default=0)),
                ('transaction_number', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined')], default='pending', max_length=50)),
                ('data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Rejects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('course', 'course'), ('blogs', 'blogs'), ('blog_payment', 'blog_payment'), ('consultant_payment', 'consultant_payment'), ('events', 'events'), ('payment', 'payment'), ('teacher', 'teacher'), ('add_user', 'add_user')], max_length=50)),
                ('content_id', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
