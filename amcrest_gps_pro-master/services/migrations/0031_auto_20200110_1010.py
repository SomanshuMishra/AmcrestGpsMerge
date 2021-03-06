# Generated by Django 2.1.4 on 2020-01-10 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0030_devicecommandslist'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='devicecommands',
            index=models.Index(fields=['imei', 'command', 'customer_id'], name='imei_comman_imei_04b121_idx'),
        ),
        migrations.AddIndex(
            model_name='devicecommandslist',
            index=models.Index(fields=['device_model', 'device_command'], name='device_comm_device__e6794c_idx'),
        ),
    ]
