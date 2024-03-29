# Generated by Django 3.2.8 on 2022-04-06 17:32

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
            name='Audio_Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.TextField()),
                ('duration', models.PositiveIntegerField(null=True)),
                ('is_play', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Audio_Tracks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='')),
                ('price', models.FloatField(null=True)),
                ('data', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('buyers', models.ManyToManyField(blank=True, related_name='exist_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('library', models.IntegerField(choices=[(1, 'audio_book'), (2, 'music'), (3, 'movies'), (4, 'e_book')], default=1)),
                ('content_id', models.IntegerField(null=True)),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.TextField()),
                ('duration', models.PositiveIntegerField(null=True)),
                ('is_play', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('track', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='music_track', to='library.audio_tracks')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Movies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.TextField()),
                ('duration', models.PositiveIntegerField(null=True)),
                ('price', models.FloatField(null=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('buyers', models.ManyToManyField(blank=True, related_name='movies_user', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.category')),
                ('comments', models.ManyToManyField(blank=True, to='library.Comments')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Library_Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('bank', 'bank'), ('Western Union', 'Western Union'), ('Paypal', 'Paypal')], max_length=100)),
                ('library_type', models.IntegerField(choices=[(1, 'audio_book'), (2, 'music'), (3, 'movies'), (4, 'e_book')], default=3)),
                ('payment_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('transaction_number', models.CharField(max_length=50, null=True)),
                ('amount', models.PositiveIntegerField(default=0)),
                ('content_id', models.IntegerField()),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=10)),
                ('created_at', models.DateField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='E_Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.TextField()),
                ('price', models.FloatField(null=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='audio_tracks',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.category'),
        ),
        migrations.AddField(
            model_name='audio_tracks',
            name='comments',
            field=models.ManyToManyField(blank=True, to='library.Comments'),
        ),
        migrations.AddField(
            model_name='audio_tracks',
            name='music',
            field=models.ManyToManyField(blank=True, to='library.Music'),
        ),
        migrations.AddField(
            model_name='audio_tracks',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Audio_Book_Tracks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='')),
                ('price', models.FloatField(null=True)),
                ('data', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('book', models.ManyToManyField(blank=True, to='library.Audio_Book')),
                ('buyers', models.ManyToManyField(blank=True, related_name='audio_book_user', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.category')),
                ('comments', models.ManyToManyField(blank=True, to='library.Comments')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='audio_book',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='audio_book_track', to='library.audio_book_tracks'),
        ),
        migrations.AddField(
            model_name='audio_book',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=10)),
                ('data', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
