# Generated by Django 2.1.4 on 2019-11-05 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0048_zonealert_category'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='zonealert',
            name='zone_alert_custome_3f3aa6_idx',
        ),
        migrations.AddIndex(
            model_name='zonealert',
            index=models.Index(fields=['customer_id', 'created_on', 'name', 'zone', 'imei', 'category'], name='zone_alert_custome_5320d0_idx'),
        ),
    ]