# Generated by Django 2.1.4 on 2019-05-29 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0010_delete_tripcalculationgldata'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuffGLFriMarkers',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('report_name', models.CharField(blank=True, max_length=20, null=True)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('report_id', models.CharField(blank=True, max_length=5, null=True)),
                ('report_type', models.CharField(blank=True, max_length=5, null=True)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('gps_accuracy', models.IntegerField(blank=True, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('azimuth', models.CharField(blank=True, max_length=5, null=True)),
                ('altitude', models.CharField(blank=True, max_length=10, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=14, null=True)),
                ('mcc', models.CharField(blank=True, max_length=5, null=True)),
                ('mnc', models.CharField(blank=True, max_length=5, null=True)),
                ('lac', models.CharField(blank=True, max_length=5, null=True)),
                ('ceil_id', models.CharField(blank=True, max_length=5, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('battery_percentage', models.IntegerField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('tail', models.CharField(blank=True, max_length=5, null=True)),
                ('location_status', models.IntegerField(blank=True, null=True)),
                ('record_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'buff_gl_fri_markers',
            },
        ),
        migrations.CreateModel(
            name='BuffSttMarkers',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('report_name', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=8, null=True)),
                ('imei', models.CharField(blank=True, max_length=20, null=True)),
                ('device_name', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.IntegerField(null=True)),
                ('gps_accuracy', models.CharField(blank=True, max_length=2, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('azimuth', models.CharField(blank=True, max_length=4, null=True)),
                ('altitude', models.CharField(blank=True, max_length=8, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('gps_utc_time', models.CharField(blank=True, max_length=20, null=True)),
                ('mcc', models.CharField(blank=True, max_length=4, null=True)),
                ('mnc', models.CharField(blank=True, max_length=4, null=True)),
                ('lac', models.CharField(blank=True, max_length=4, null=True)),
                ('ceil_id', models.CharField(blank=True, max_length=4, null=True)),
                ('mileage', models.FloatField(blank=True, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('tail', models.CharField(blank=True, max_length=5, null=True)),
                ('location_status', models.IntegerField(blank=True, default=0, null=True)),
                ('alert_status', models.IntegerField(blank=True, default=0, null=True)),
                ('record_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'buff_stt_markers',
            },
        ),
        migrations.AddIndex(
            model_name='buffsttmarkers',
            index=models.Index(fields=['date', 'imei', 'device_name', 'longitude', 'latitude', 'gps_utc_time', 'send_time', 'record_date'], name='buff_stt_ma_date_9e6574_idx'),
        ),
        migrations.AddIndex(
            model_name='buffglfrimarkers',
            index=models.Index(fields=['date', 'imei', 'send_time', 'longitude', 'latitude', 'gps_accuracy', 'gps_utc_time', 'record_date'], name='buff_gl_fri_date_725f86_idx'),
        ),
    ]