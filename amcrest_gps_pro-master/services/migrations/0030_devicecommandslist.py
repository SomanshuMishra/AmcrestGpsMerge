# Generated by Django 2.1.4 on 2020-01-08 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0029_auto_20191226_0840'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceCommandsList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_model', models.CharField(max_length=20)),
                ('device_command', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'device_command_list',
                'managed': True,
            },
        ),
    ]
