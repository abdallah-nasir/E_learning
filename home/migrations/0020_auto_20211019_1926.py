# Generated by Django 3.2.8 on 2021-10-19 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_branch_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('place', models.CharField(max_length=100)),
                ('map', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='branch',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
