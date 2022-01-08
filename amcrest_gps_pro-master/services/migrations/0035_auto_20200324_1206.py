# Generated by Django 2.1.4 on 2020-03-24 12:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0034_auto_20200316_0903'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='feedbackmodel',
            name='feedback_ta_rating_91847c_idx',
        ),
        migrations.AddField(
            model_name='feedbackmodel',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='feedbackmodel',
            index=models.Index(fields=['rating', 'email', 'record_date'], name='feedback_ta_rating_ba7355_idx'),
        ),
    ]
