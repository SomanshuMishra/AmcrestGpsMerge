# Generated by Django 2.1.4 on 2019-04-03 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0005_auto_20190403_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='glfrimarkers',
            name='report_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
