# Generated by Django 3.2.8 on 2022-02-02 18:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Consultant', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cosultant_payment',
            name='consultant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Consultant.consultant'),
        ),
    ]
