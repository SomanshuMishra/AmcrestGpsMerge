# Generated by Django 2.1.4 on 2019-04-05 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20190327_0950'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(max_length=10)),
                ('body', models.TextField(blank=True, null=True)),
                ('title', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'notification_message',
                'managed': True,
            },
        ),
        migrations.AddIndex(
            model_name='notificationmessage',
            index=models.Index(fields=['protocol'], name='notificatio_protoco_4b439e_idx'),
        ),
    ]