# Generated by Django 2.1.4 on 2019-08-13 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0019_auto_20190805_1603'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='obdmarkers',
            name='obd_markers_date_94d5ff_idx',
        ),
        migrations.RenameField(
            model_name='obdmarkers',
            old_name='fuel_consuption',
            new_name='fuel_consumption',
        ),
        migrations.AddIndex(
            model_name='obdmarkers',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'engine_rpm', 'vehicle_speed', 'engine_coolant_temp', 'fuel_consumption', 'throttle_position', 'engine_load', 'record_date'], name='obd_markers_date_c1b50e_idx'),
        ),
    ]