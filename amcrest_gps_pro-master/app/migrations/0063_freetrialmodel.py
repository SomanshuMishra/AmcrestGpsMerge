# Generated by Django 2.1.4 on 2020-02-13 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0062_zonealertobd_zone_device_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeTrialModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=30)),
                ('customer_id', models.CharField(max_length=50)),
                ('free_trial_month', models.IntegerField()),
                ('record_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
