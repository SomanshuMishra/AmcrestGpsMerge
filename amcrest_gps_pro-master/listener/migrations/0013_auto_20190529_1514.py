# Generated by Django 2.1.4 on 2019-05-29 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0012_auto_20190529_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sttmarkers',
            name='ceil_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]