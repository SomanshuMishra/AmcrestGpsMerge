# Generated by Django 2.1.4 on 2019-11-25 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0054_reviewtable_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewtable',
            name='category',
            field=models.CharField(default='gps', max_length=20),
            preserve_default=False,
        ),
    ]
