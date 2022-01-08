# Generated by Django 2.1.4 on 2019-11-27 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0025_auto_20191126_0651'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amcrest_gps_android', models.CharField(blank=True, max_length=20, null=True)),
                ('amcrest_gps_ios', models.CharField(blank=True, max_length=20, null=True)),
                ('amcrest_obd_android', models.CharField(blank=True, max_length=20, null=True)),
                ('amcrest_obd_ios', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'app_version',
                'managed': True,
            },
        ),
    ]
