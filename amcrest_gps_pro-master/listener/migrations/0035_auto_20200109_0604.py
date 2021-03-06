# Generated by Django 2.1.4 on 2020-01-09 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0034_auto_20200107_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoFenceAck',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=15, null=True)),
                ('geo_id', models.CharField(blank=True, max_length=5, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('count_number', models.CharField(blank=True, max_length=10, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
                ('record_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'geofence_obd_ack',
            },
        ),
        migrations.AddIndex(
            model_name='geofenceack',
            index=models.Index(fields=['date', 'imei', 'device_name', 'send_time', 'protocol', 'record_date'], name='geofence_ob_date_0118a5_idx'),
        ),
    ]
