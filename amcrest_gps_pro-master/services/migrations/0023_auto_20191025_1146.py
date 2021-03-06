# Generated by Django 2.1.4 on 2019-10-25 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0022_auto_20191016_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceNotReportingAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=30)),
                ('record_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'device_not_reporting_alert',
                'managed': True,
            },
        ),
        migrations.AddIndex(
            model_name='devicenotreportingalert',
            index=models.Index(fields=['imei', 'record_date'], name='device_not__imei_3cb0d6_idx'),
        ),
    ]
