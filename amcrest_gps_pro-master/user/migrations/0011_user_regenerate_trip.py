# Generated by Django 2.1.4 on 2020-09-02 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_user_time_format'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='regenerate_trip',
            field=models.BooleanField(default=False),
        ),
    ]
