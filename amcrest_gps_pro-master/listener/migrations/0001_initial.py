# Generated by Django 2.1.4 on 2019-03-08 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttachDettach',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=15, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=10, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=14, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=4, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'db_table': 'attach_dettach',
            },
        ),
        migrations.CreateModel(
            name='BatteryLow',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=15, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('battery_backup_voltage', models.FloatField(blank=True, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=20, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=10, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'db_table': 'battery_low',
            },
        ),
        migrations.CreateModel(
            name='CrashReport',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=15, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=20, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=10, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'db_table': 'crash_report',
            },
        ),
        migrations.CreateModel(
            name='EngineSummary',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('journey_fuel_consumption', models.FloatField(blank=True, null=True)),
                ('max_rpm', models.FloatField(blank=True, null=True)),
                ('average_rpm', models.FloatField(blank=True, null=True)),
                ('max_throttle_position', models.FloatField(blank=True, null=True)),
                ('average_throttle_position', models.FloatField(blank=True, null=True)),
                ('max_engine_load', models.FloatField(blank=True, null=True)),
                ('average_engine_load', models.FloatField(blank=True, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=20, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=10, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
                ('created_date', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'engine_summary',
            },
        ),
        migrations.CreateModel(
            name='FriMarkers',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('extrnal_power_voltage', models.FloatField(blank=True, null=True)),
                ('report_id', models.CharField(blank=True, max_length=5, null=True)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=14, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('hour_meter_count', models.CharField(blank=True, max_length=15, null=True)),
                ('backup_battery_percentage', models.IntegerField(blank=True, null=True)),
                ('device_status', models.CharField(blank=True, max_length=10, null=True)),
                ('engine_rpm', models.FloatField(blank=True, null=True)),
                ('fuel_consumption', models.CharField(blank=True, max_length=10, null=True)),
                ('fuel_level_input', models.FloatField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=10, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'db_table': 'fri_markers',
            },
        ),
        migrations.CreateModel(
            name='HarshBehaviour',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('report_type', models.CharField(blank=True, max_length=3, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=14, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=10, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'db_table': 'harsh_behaviour',
            },
        ),
        migrations.CreateModel(
            name='IgnitionOnoff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=15, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=20, null=True)),
                ('duration_of_ignition_off', models.CharField(blank=True, max_length=20, null=True)),
                ('gps_accuracy', models.CharField(blank=True, max_length=5, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=20, null=True)),
                ('hour_meter_count', models.CharField(blank=True, max_length=15, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=5, null=True)),
            ],
            options={
                'db_table': 'ignition_onoff',
            },
        ),
        migrations.CreateModel(
            name='ObdMarkers',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=15, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('obd_connection', models.IntegerField(blank=True, null=True)),
                ('obd_power_voltage', models.FloatField(blank=True, null=True)),
                ('supported_pid', models.CharField(blank=True, max_length=10, null=True)),
                ('engine_rpm', models.FloatField(blank=True, null=True)),
                ('vehicle_speed', models.FloatField(blank=True, null=True)),
                ('engine_coolant_temp', models.FloatField(blank=True, null=True)),
                ('fuel_consuption', models.CharField(blank=True, max_length=10, null=True)),
                ('dtc_cleared_distance', models.FloatField(blank=True, null=True)),
                ('mil_activated_distance', models.FloatField(blank=True, null=True)),
                ('mil_status', models.IntegerField(blank=True, null=True)),
                ('number_of_dtc', models.IntegerField(blank=True, null=True)),
                ('dignostic_trouble_codes', models.CharField(blank=True, max_length=6, null=True)),
                ('throttle_position', models.FloatField(blank=True, null=True)),
                ('engine_load', models.FloatField(blank=True, null=True)),
                ('fuel_level_input', models.FloatField(blank=True, null=True)),
                ('obd_protocol', models.CharField(blank=True, max_length=1, null=True)),
                ('obd_mileage', models.FloatField(blank=True, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=20, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=6, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'db_table': 'obd_markers',
            },
        ),
        migrations.CreateModel(
            name='ObdStatusReport',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('obd_connection', models.IntegerField(blank=True, null=True)),
                ('obd_power_voltage', models.FloatField(blank=True, null=True)),
                ('supported_pid', models.CharField(blank=True, max_length=10, null=True)),
                ('engine_rpm', models.FloatField(blank=True, null=True)),
                ('vehicle_speed', models.FloatField(blank=True, null=True)),
                ('engine_coolant_temp', models.FloatField(blank=True, null=True)),
                ('fuel_consumption', models.CharField(blank=True, max_length=10, null=True)),
                ('dtc_cleared_distance', models.FloatField(blank=True, null=True)),
                ('mil_activated_distance', models.FloatField(blank=True, null=True)),
                ('mil_status', models.IntegerField(blank=True, null=True)),
                ('number_of_dtc', models.IntegerField(blank=True, null=True)),
                ('dignostic_trouble_codes', models.CharField(blank=True, max_length=6, null=True)),
                ('throttle_position', models.FloatField(blank=True, null=True)),
                ('engine_load', models.FloatField(blank=True, null=True)),
                ('fuel_level_input', models.FloatField(blank=True, null=True)),
                ('obd_protocol', models.CharField(blank=True, max_length=1, null=True)),
                ('obd_mileage', models.FloatField(blank=True, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=20, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=6, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'db_table': 'obd_status_report',
            },
        ),
        migrations.AddIndex(
            model_name='obdstatusreport',
            index=models.Index(fields=['date', 'imei', 'device_name', 'obd_protocol', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol'], name='obd_status__date_07bbbb_idx'),
        ),
        migrations.AddIndex(
            model_name='obdmarkers',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'engine_rpm', 'vehicle_speed', 'engine_coolant_temp', 'fuel_consuption', 'throttle_position', 'engine_load'], name='obd_markers_date_adf941_idx'),
        ),
        migrations.AddIndex(
            model_name='ignitiononoff',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol'], name='ignition_on_date_bdbb8d_idx'),
        ),
        migrations.AddIndex(
            model_name='harshbehaviour',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol'], name='harsh_behav_date_43bae7_idx'),
        ),
        migrations.AddIndex(
            model_name='frimarkers',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol'], name='fri_markers_date_16a680_idx'),
        ),
        migrations.AddIndex(
            model_name='enginesummary',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'created_date'], name='engine_summ_date_716dbb_idx'),
        ),
        migrations.AddIndex(
            model_name='crashreport',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol'], name='crash_repor_date_1d80d8_idx'),
        ),
        migrations.AddIndex(
            model_name='batterylow',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol'], name='battery_low_date_3616ca_idx'),
        ),
        migrations.AddIndex(
            model_name='attachdettach',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol'], name='attach_dett_date_e5a77f_idx'),
        ),
    ]
