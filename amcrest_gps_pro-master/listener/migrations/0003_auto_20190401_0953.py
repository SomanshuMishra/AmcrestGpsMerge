# Generated by Django 2.1.4 on 2019-04-01 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0002_auto_20190331_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='GLFriMarkers',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
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
            ],
            options={
                'db_table': 'gl_fri_markers',
            },
        ),
        migrations.AddIndex(
            model_name='glfrimarkers',
            index=models.Index(fields=['date', 'imei', 'send_time', 'longitude', 'latitude', 'gps_accuracy', 'gps_utc_time'], name='gl_fri_mark_date_9768ee_idx'),
        ),
    ]
