# Generated by Django 3.2.8 on 2021-11-30 11:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Rejects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('course', 'course'), ('blogs', 'blogs'), ('blog_payment', 'blog_payment'), ('consultant_payment', 'consultant_payment'), ('events', 'events'), ('payment', 'payment'), ('teacher', 'teacher')], max_length=50)),
                ('content_id', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]