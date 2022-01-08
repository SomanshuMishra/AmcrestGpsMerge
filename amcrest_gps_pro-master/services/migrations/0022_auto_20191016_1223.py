# Generated by Django 2.1.4 on 2019-10-16 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0021_simmapping_subscription_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DtcRecords',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtc_code', models.CharField(blank=True, max_length=50)),
                ('dtc_short_description', models.TextField(null=True)),
                ('error_code_url', models.CharField(blank=True, max_length=500, null=True)),
                ('severity_level', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'DTC Record',
                'verbose_name_plural': 'DTC Records',
                'db_table': 'dtc_records',
                'managed': True,
            },
        ),
        migrations.AddIndex(
            model_name='dtcrecords',
            index=models.Index(fields=['dtc_code'], name='dtc_records_dtc_cod_0d7b9e_idx'),
        ),
    ]