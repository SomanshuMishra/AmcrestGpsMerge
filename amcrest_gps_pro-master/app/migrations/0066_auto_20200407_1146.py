# Generated by Django 2.1.4 on 2020-04-07 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0065_auto_20200323_0736'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuelConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=20)),
                ('consumption', models.FloatField(null=True)),
                ('record_date', models.DateField(null=True)),
                ('customer_id', models.BigIntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'fuel_consumption',
                'managed': True,
            },
        ),
    ]