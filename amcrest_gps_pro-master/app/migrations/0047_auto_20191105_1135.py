# Generated by Django 2.1.4 on 2019-11-05 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20191101_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settingsmodel',
            name='trip_coordinate',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='trip_sensor',
            field=models.BooleanField(default=False),
        ),
    ]
