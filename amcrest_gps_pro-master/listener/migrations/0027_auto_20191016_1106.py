# Generated by Django 2.1.4 on 2019-10-16 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0026_auto_20191016_0737'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dtcrecords',
            name='checksum',
        ),
        migrations.RemoveField(
            model_name='dtcrecords',
            name='obd_header',
        ),
        migrations.RemoveField(
            model_name='dtcrecords',
            name='obd_message_type',
        ),
        migrations.AlterField(
            model_name='dtcrecords',
            name='sae_standard',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
