# Generated by Django 2.1.4 on 2020-01-23 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0060_auto_20200121_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='zoneobd',
            name='radius',
            field=models.FloatField(default=50),
            preserve_default=False,
        ),
    ]
