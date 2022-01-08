# Generated by Django 2.1.4 on 2021-04-28 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_auto_20210127_1131'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='user_user_email_5f6a77_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['customer_id'], name='user_user_custome_b66cda_idx'),
        ),
    ]