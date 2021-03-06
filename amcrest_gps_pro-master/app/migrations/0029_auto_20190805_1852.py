# Generated by Django 2.1.4 on 2019-08-05 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_auto_20190625_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='settingsmodel',
            name='tow_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='settingsmodel',
            name='tow_notification',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='settingsmodel',
            name='tow_sms',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
