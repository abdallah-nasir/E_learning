# Generated by Django 3.2.8 on 2021-10-20 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_auto_20211020_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='videos',
            field=models.ManyToManyField(to='home.Videos'),
        ),
        migrations.AlterField(
            model_name='videos',
            name='my_course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course', to='home.course'),
        ),
    ]
