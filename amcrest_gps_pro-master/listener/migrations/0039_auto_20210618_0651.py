# Generated by Django 2.1.4 on 2021-06-18 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0038_auto_20210428_0717'),
    ]

    operations = [
        migrations.CreateModel(
            name='OBDTCRecords',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.CharField(blank=True, max_length=20, null=True)),
                ('time', models.CharField(blank=True, max_length=20, null=True)),
                ('protocol', models.CharField(blank=True, max_length=12, null=True)),
                ('count_number', models.CharField(blank=True, max_length=6, null=True)),
                ('protocol_version', models.CharField(blank=True, max_length=10, null=True)),
                ('imei', models.CharField(max_length=20)),
                ('warning_code', models.CharField(blank=True, max_length=12, null=True)),
                ('warning_value', models.CharField(blank=True, max_length=12, null=True)),
                ('warning_details', models.CharField(blank=True, max_length=240, null=True)),
                ('send_time', models.BigIntegerField(blank=True, null=True)),
                ('record_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'obd_dignosis_trouble_code',
            },
        ),
        migrations.AddIndex(
            model_name='obdtcrecords',
            index=models.Index(fields=['date', 'imei', 'send_time', 'record_date'], name='obd_dignosi_date_16e1a9_idx'),
        ),
    ]
