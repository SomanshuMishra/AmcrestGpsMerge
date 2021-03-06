# Generated by Django 2.1.4 on 2019-09-12 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_auto_20190906_0525'),
    ]

    operations = [
        migrations.AddField(
            model_name='settingsmodel',
            name='secondary_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='global_notification',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='harshacceleration_notification',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='harshbraking_notification',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='harshturning_notification',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='sos_email',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='sos_sms',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='speed_notification',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='tow_email',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='tow_sms',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='settingsmodel',
            name='zone_alert_notification',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
