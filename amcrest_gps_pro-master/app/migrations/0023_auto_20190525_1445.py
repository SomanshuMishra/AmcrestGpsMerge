# Generated by Django 2.1.4 on 2019-05-25 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20190525_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settingsmodel',
            name='imei',
            field=models.CharField(max_length=25, unique=True),
        ),
    ]
