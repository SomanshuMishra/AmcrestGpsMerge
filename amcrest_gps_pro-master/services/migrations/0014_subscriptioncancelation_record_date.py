# Generated by Django 2.1.4 on 2019-04-15 07:02

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_auto_20190411_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptioncancelation',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2019, 4, 15, 7, 2, 40, 21329, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
