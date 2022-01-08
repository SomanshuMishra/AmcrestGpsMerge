# Generated by Django 2.1.4 on 2019-04-03 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0004_auto_20190402_0727'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='attachdettach',
            name='attach_dett_date_e5a77f_idx',
        ),
        migrations.RemoveIndex(
            model_name='batterylow',
            name='battery_low_date_3616ca_idx',
        ),
        migrations.RemoveIndex(
            model_name='batterymodel',
            name='battery_ono_date_ec6444_idx',
        ),
        migrations.RemoveIndex(
            model_name='crashreport',
            name='crash_repor_date_1d80d8_idx',
        ),
        migrations.RemoveIndex(
            model_name='enginesummary',
            name='engine_summ_date_716dbb_idx',
        ),
        migrations.RemoveIndex(
            model_name='frimarkers',
            name='fri_markers_date_16a680_idx',
        ),
        migrations.RemoveIndex(
            model_name='glfrimarkers',
            name='gl_fri_mark_date_9768ee_idx',
        ),
        migrations.RemoveIndex(
            model_name='harshbehaviour',
            name='harsh_behav_date_43bae7_idx',
        ),
        migrations.RemoveIndex(
            model_name='ignitiononoff',
            name='ignition_on_date_bdbb8d_idx',
        ),
        migrations.RemoveIndex(
            model_name='obdmarkers',
            name='obd_markers_date_adf941_idx',
        ),
        migrations.RemoveIndex(
            model_name='obdstatusreport',
            name='obd_status__date_07bbbb_idx',
        ),
        migrations.RemoveIndex(
            model_name='power',
            name='power_onoff_date_d67b98_idx',
        ),
        migrations.RemoveIndex(
            model_name='sos',
            name='sos_markers_date_4846dd_idx',
        ),
        migrations.RemoveIndex(
            model_name='sttmarkers',
            name='stt_markers_date_f5f79c_idx',
        ),
        migrations.AddField(
            model_name='attachdettach',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='batterylow',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='batterymodel',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='crashreport',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='enginesummary',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='frimarkers',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='glfrimarkers',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='harshbehaviour',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='ignitiononoff',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='obdmarkers',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='obdstatusreport',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='power',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='sos',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='sttmarkers',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddIndex(
            model_name='attachdettach',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'record_date'], name='attach_dett_date_b0d9c6_idx'),
        ),
        migrations.AddIndex(
            model_name='batterylow',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'record_date'], name='battery_low_date_551362_idx'),
        ),
        migrations.AddIndex(
            model_name='batterymodel',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'gps_accuracy', 'speed', 'record_date'], name='battery_ono_date_e0e59f_idx'),
        ),
        migrations.AddIndex(
            model_name='crashreport',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'record_date'], name='crash_repor_date_6e015a_idx'),
        ),
        migrations.AddIndex(
            model_name='enginesummary',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'created_date', 'record_date'], name='engine_summ_date_334797_idx'),
        ),
        migrations.AddIndex(
            model_name='frimarkers',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'record_date'], name='fri_markers_date_fc0e42_idx'),
        ),
        migrations.AddIndex(
            model_name='glfrimarkers',
            index=models.Index(fields=['date', 'imei', 'send_time', 'longitude', 'latitude', 'gps_accuracy', 'gps_utc_time', 'record_date'], name='gl_fri_mark_date_4484fb_idx'),
        ),
        migrations.AddIndex(
            model_name='harshbehaviour',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'record_date'], name='harsh_behav_date_ffc09d_idx'),
        ),
        migrations.AddIndex(
            model_name='ignitiononoff',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'record_date'], name='ignition_on_date_b37af3_idx'),
        ),
        migrations.AddIndex(
            model_name='obdmarkers',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'engine_rpm', 'vehicle_speed', 'engine_coolant_temp', 'fuel_consuption', 'throttle_position', 'engine_load', 'record_date'], name='obd_markers_date_94d5ff_idx'),
        ),
        migrations.AddIndex(
            model_name='obdstatusreport',
            index=models.Index(fields=['date', 'imei', 'device_name', 'obd_protocol', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'protocol', 'record_date'], name='obd_status__date_b15f00_idx'),
        ),
        migrations.AddIndex(
            model_name='power',
            index=models.Index(fields=['date', 'imei', 'device_name', 'send_time', 'record_date'], name='power_onoff_date_a1c19d_idx'),
        ),
        migrations.AddIndex(
            model_name='sos',
            index=models.Index(fields=['date', 'imei', 'device_name', 'send_time', 'gps_utc_time', 'speed', 'longitude', 'latitude', 'record_date'], name='sos_markers_date_bb1143_idx'),
        ),
        migrations.AddIndex(
            model_name='sttmarkers',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'record_date'], name='stt_markers_date_4e8206_idx'),
        ),
    ]