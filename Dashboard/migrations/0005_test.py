# Generated by Django 3.2.8 on 2022-02-09 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0010_auto_20220209_0048'),
        ('Dashboard', '0004_alter_refunds_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.ManyToManyField(blank=True, to='taggit.Tag')),
            ],
        ),
    ]
