# Generated by Django 2.1.4 on 2019-12-03 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0027_auto_20191203_1023'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='serviceplanobd',
            name='service_pla_service_0796e7_idx',
        ),
        migrations.AddField(
            model_name='serviceplanobd',
            name='base_device_frequency',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddIndex(
            model_name='serviceplanobd',
            index=models.Index(fields=['service_plan_id', 'base_device_frequency'], name='service_pla_service_b24404_idx'),
        ),
    ]
