# Generated by Django 3.2.8 on 2022-02-02 13:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Consultant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdataform',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='teacher_time',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Consultant.category'),
        ),
        migrations.AddField(
            model_name='teacher_time',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cosultant_payment',
            name='consultant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Consultant.consultant'),
        ),
        migrations.AddField(
            model_name='cosultant_payment',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Consultant.teacher_time'),
        ),
        migrations.AddField(
            model_name='cosultant_payment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='consultant',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Consultant.teacher_time'),
        ),
        migrations.AddField(
            model_name='consultant',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
