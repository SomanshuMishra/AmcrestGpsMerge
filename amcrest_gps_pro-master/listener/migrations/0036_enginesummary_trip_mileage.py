# Generated by Django 2.1.4 on 2020-01-17 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0035_auto_20200109_0604'),
    ]

    operations = [
        migrations.AddField(
            model_name='enginesummary',
            name='trip_mileage',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
