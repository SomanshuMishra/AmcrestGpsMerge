# Generated by Django 2.1.4 on 2019-05-02 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0008_auto_20190430_1020'),
    ]

    operations = [
        migrations.CreateModel(
            name='TripCalculationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=20)),
                ('_details', models.TextField(blank=True, db_column='details', null=True)),
            ],
            options={
                'db_table': 'trip_calculation_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TripCalculationGLData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=20)),
                ('_details', models.TextField(blank=True, db_column='details', null=True)),
            ],
            options={
                'db_table': 'trip_calculation_data_gl',
                'managed': True,
            },
        ),
        migrations.AddIndex(
            model_name='tripcalculationgldata',
            index=models.Index(fields=['imei'], name='trip_calcul_imei_0c18d8_idx'),
        ),
        migrations.AddIndex(
            model_name='tripcalculationdata',
            index=models.Index(fields=['imei'], name='trip_calcul_imei_118346_idx'),
        ),
    ]
