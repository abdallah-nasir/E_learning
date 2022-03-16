# Generated by Django 3.2.8 on 2022-03-16 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0008_auto_20220316_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio_book',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='e_book',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='movies',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='music',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('refund', 'refund')], default='pending', max_length=20),
        ),
    ]