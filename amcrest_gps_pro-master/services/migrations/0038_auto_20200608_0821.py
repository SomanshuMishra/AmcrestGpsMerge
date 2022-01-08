# Generated by Django 2.1.4 on 2020-06-08 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0037_devicecommands_record_date'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='feedbackmodel',
            name='feedback_ta_rating_ba7355_idx',
        ),
        migrations.RemoveIndex(
            model_name='feedbackskipped',
            name='skipped_fee_email_6bc4f9_idx',
        ),
        migrations.AddField(
            model_name='feedbackmodel',
            name='category',
            field=models.CharField(default='gps', max_length=20),
        ),
        migrations.AddField(
            model_name='feedbackskipped',
            name='category',
            field=models.CharField(default='gps', max_length=20),
        ),
        migrations.AddIndex(
            model_name='feedbackmodel',
            index=models.Index(fields=['rating', 'email', 'record_date', 'category'], name='feedback_ta_rating_0cc815_idx'),
        ),
        migrations.AddIndex(
            model_name='feedbackskipped',
            index=models.Index(fields=['email', 'created_date', 'category'], name='skipped_fee_email_cbf6ae_idx'),
        ),
    ]