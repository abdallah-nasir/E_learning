# Generated by Django 3.2.8 on 2022-03-18 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0015_auto_20220318_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='library_payment',
            name='content_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
