# Generated by Django 2.1.4 on 2020-01-24 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0061_zoneobd_radius'),
    ]

    operations = [
        migrations.AddField(
            model_name='zonealertobd',
            name='zone_device_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
