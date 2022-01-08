# Generated by Django 2.1.4 on 2019-03-08 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_name', models.CharField(max_length=50)),
                ('key_value', models.CharField(max_length=500)),
                ('base64_value', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'app_configuration',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Countries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(blank=True, max_length=50, null=True)),
                ('country_iso_code', models.CharField(blank=True, max_length=5, null=True)),
                ('country_iso_code_2', models.CharField(blank=True, max_length=5, null=True)),
            ],
            options={
                'verbose_name': 'Countries',
                'verbose_name_plural': 'Countries',
                'db_table': 'countries',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HarshNotificationMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(max_length=3)),
                ('body', models.TextField(blank=True, null=True)),
                ('title', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'harsh_notification_message',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Langauges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=10, null=True)),
                ('value', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Langauges',
                'verbose_name_plural': 'Langauges',
                'db_table': 'langauges',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ServicePlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_plan_id', models.CharField(max_length=50)),
                ('service_plan_name', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('duration', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'ServicePlan',
                'verbose_name_plural': 'ServicePlans',
                'db_table': 'service_plan',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SimMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=15)),
                ('iccid', models.CharField(max_length=25)),
                ('model', models.CharField(max_length=15)),
                ('duration_type', models.IntegerField(default=0)),
                ('record_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'SimMapping',
                'verbose_name_plural': 'SimMapping',
                'db_table': 'sim_mapping',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SimUpdateCredentials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('api_key', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': 'SimUpdateCredentials',
                'verbose_name_plural': 'SimUpdateCredentials',
                'db_table': 'sim_update_credentials',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='States',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=5, null=True)),
                ('state_code', models.CharField(blank=True, max_length=5, null=True)),
                ('state_name', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'States',
                'verbose_name_plural': 'States',
                'db_table': 'states',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SubscriptionCancelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('imei', models.CharField(blank=True, max_length=20, null=True)),
                ('cancelation_reason', models.CharField(blank=True, max_length=1000, null=True)),
                ('how_gps_tracker', models.CharField(blank=True, max_length=1000, null=True)),
                ('comment', models.CharField(blank=True, max_length=500, null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('customer_id', models.CharField(blank=True, max_length=50, null=True)),
                ('subscription_id', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'subscription_cancelation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TimeZoneModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_code', models.CharField(blank=True, max_length=10, null=True)),
                ('time_zone', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'TimeZoneModel',
                'verbose_name_plural': 'TimeZoneModel',
                'db_table': 'time_zones',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='WebhookSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('webhook_date_recieved', models.DateTimeField(null=True)),
                ('kind', models.CharField(blank=True, max_length=200, null=True)),
                ('subscription_id', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'webhook_log',
                'managed': True,
            },
        ),
        migrations.AddIndex(
            model_name='webhooksubscription',
            index=models.Index(fields=['webhook_date_recieved', 'kind', 'subscription_id'], name='webhook_log_webhook_0ffefd_idx'),
        ),
        migrations.AddIndex(
            model_name='timezonemodel',
            index=models.Index(fields=['time_zone', 'country_code'], name='time_zones_time_zo_178a98_idx'),
        ),
        migrations.AddIndex(
            model_name='subscriptioncancelation',
            index=models.Index(fields=['imei'], name='subscriptio_imei_a7415b_idx'),
        ),
        migrations.AddIndex(
            model_name='states',
            index=models.Index(fields=['state_code', 'state_name', 'country'], name='states_state_c_662553_idx'),
        ),
        migrations.AddIndex(
            model_name='simmapping',
            index=models.Index(fields=['imei', 'model', 'duration_type'], name='sim_mapping_imei_f5d156_idx'),
        ),
        migrations.AddIndex(
            model_name='serviceplan',
            index=models.Index(fields=['service_plan_id'], name='service_pla_service_b3fb1e_idx'),
        ),
        migrations.AddIndex(
            model_name='langauges',
            index=models.Index(fields=['code', 'value'], name='langauges_code_7c6338_idx'),
        ),
        migrations.AddIndex(
            model_name='harshnotificationmessage',
            index=models.Index(fields=['report_type'], name='harsh_notif_report__2f9f5f_idx'),
        ),
        migrations.AddIndex(
            model_name='countries',
            index=models.Index(fields=['country_name', 'country_iso_code'], name='countries_country_48f60e_idx'),
        ),
        migrations.AddIndex(
            model_name='appconfiguration',
            index=models.Index(fields=['key_name'], name='app_configu_key_nam_99712a_idx'),
        ),
    ]
