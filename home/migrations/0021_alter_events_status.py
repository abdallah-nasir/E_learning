# Generated by Django 3.2.8 on 2021-12-11 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_auto_20211210_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='status',
            field=models.CharField(choices=[('approved', 'approved'), ('declined', 'declined'), ('pending', 'pending'), ('completed', 'completed')], default='pending', max_length=20),
        ),
    ]
