# Generated by Django 2.1.4 on 2019-08-12 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_auto_20190807_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settingsmodel',
            name='email',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='phone',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
