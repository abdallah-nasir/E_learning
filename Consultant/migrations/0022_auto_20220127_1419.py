# Generated by Django 3.2.8 on 2022-01-27 14:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Consultant', '0021_cosultant_payment_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cosultant_payment',
            old_name='data',
            new_name='user_data',
        ),
        migrations.AddField(
            model_name='consultant',
            name='user_data',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]