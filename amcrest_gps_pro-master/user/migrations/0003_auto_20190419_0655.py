# Generated by Django 2.1.4 on 2019-04-19 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20190417_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='later_flag',
            field=models.BigIntegerField(default=1, null=True, verbose_name='Later Flag'),
        ),
        migrations.AlterField(
            model_name='user',
            name='later_time',
            field=models.BigIntegerField(null=True, verbose_name='Later Time'),
        ),
    ]
