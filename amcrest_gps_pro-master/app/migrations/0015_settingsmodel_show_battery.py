# Generated by Django 2.1.4 on 2019-04-22 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20190417_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='settingsmodel',
            name='show_battery',
            field=models.BooleanField(default=True),
        ),
    ]
