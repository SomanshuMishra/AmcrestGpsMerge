from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password

import base64

User = get_user_model()



class SimMapping(models.Model):
	imei = models.CharField(max_length=15, null=False, blank=False)
	iccid = models.CharField(max_length=25, null=False, blank=False)
	model = models.CharField(max_length=15, null=False, blank=False)
	duration_type = models.IntegerField(default=0)
	provider = models.CharField(max_length=50, null=False, blank=False)
	promotion_name = models.CharField(max_length=200, null=True, blank=True)
	customer_group = models.CharField(max_length=200, null=True, blank=True)
	category = models.CharField(max_length=50, null=False, blank=False)
	record_date = models.DateTimeField(auto_now_add=True)
	subscription_id = models.CharField(max_length=1000, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'sim_mapping'
		indexes = [
			models.Index(fields=['imei', 'model', 'duration_type', 'category'])
		]

		verbose_name = _('SimMapping')
		verbose_name_plural = _('SimMapping')

	def __str__(self):
		return self.imei+ ' ' +self.model

class ServicePlan(models.Model):
	service_plan_id = models.CharField(max_length=50, null=False, blank=False)
	service_plan_name = models.CharField(max_length=100, null=False, blank=False)
	price = models.FloatField()
	duration = models.CharField(max_length=50, null=True, blank=True)
	base_device_frequency = models.CharField(max_length=100, null=True, blank=True)
	# service_plan

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'service_plan'
		indexes = [
			models.Index(fields=['service_plan_id', 'base_device_frequency'])
		]

		verbose_name = _('ServicePlan')
		verbose_name_plural = _('ServicePlans')

	def __str__(self):
		return self.service_plan_name+ ' : ' +self.service_plan_id+' ('+str(self.price)+')'



class ServicePlanObd(models.Model):
	service_plan_id = models.CharField(max_length=50, null=False, blank=False)
	service_plan_name = models.CharField(max_length=100, null=False, blank=False)
	price = models.FloatField()
	duration = models.CharField(max_length=50, null=True, blank=True)
	base_device_frequency = models.CharField(max_length=100, null=True, blank=True)
	# service_plan

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'service_plan_obd'
		indexes = [
			models.Index(fields=['service_plan_id', 'base_device_frequency'])
		]

		verbose_name = _('ServicePlanObd')
		verbose_name_plural = _('ServicePlansObd')

	def __str__(self):
		return self.service_plan_name+ ' : ' +self.service_plan_id+' ('+str(self.price)+')'



class Countries(models.Model):
	country_name = models.CharField(max_length=50, null=True, blank=True)
	country_iso_code = models.CharField(max_length=5, null=True, blank=True)
	country_iso_code_2 = models.CharField(max_length=5, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'countries'
		indexes = [
			models.Index(fields=['country_name', 'country_iso_code'])
		]
		verbose_name = _('Countries')
		verbose_name_plural = _('Countries')

	def __str__(self):
		return self.country_name+' ('+self.country_iso_code+')'



class States(models.Model):
	country = models.CharField(max_length=5, null=True)
	state_code = models.CharField(max_length=5, null=True, blank=True)
	state_name = models.CharField(max_length=50, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'states'
		indexes = [
			models.Index(fields=['state_code', 'state_name', 'country'])
		]

		verbose_name = _('States')
		verbose_name_plural = _('States')

	def __str__(self):
		return self.state_name

class TimeZoneModel(models.Model):
	description = models.CharField(max_length=100, null=True, blank=True)
	time_zone = models.CharField(max_length=200, null=True, blank=True)

	class Meta:
		managed=True
		app_label = 'services'
		db_table = 'time_zones'
		indexes = [
			models.Index(fields=['time_zone'])
		]
		verbose_name = _('TimeZoneModel')
		verbose_name_plural = _('TimeZoneModel')

	def __str__(self):
		return self.description + ' ('+self.time_zone+')'



class Langauges(models.Model):
	code = models.CharField(max_length=10, null=True, blank=True)
	value = models.CharField(max_length=50, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'langauges'
		indexes = [
			models.Index(fields=['code', 'value'])
		]
		verbose_name = _('Langauges')
		verbose_name_plural = _('Langauges')

	def __str__(self):
		return self.value + ' ('+self.code+')'

class HarshNotificationMessage(models.Model):
	report_type = models.CharField(max_length=3, null=False, blank=False)
	body = models.TextField(null=True, blank=True)
	title = models.TextField(null=True, blank=True)
	
	class Meta:
		managed=True
		app_label = 'services'
		db_table = 'harsh_notification_message'
		indexes = [
			models.Index(fields=['report_type'])
		]

	def __str__(self):
		return self.report_type


class NotificationMessage(models.Model):
	protocol = models.CharField(max_length=15, null=False, blank=False)
	body = models.TextField(null=True, blank=True)
	title = models.TextField(null=True, blank=True)
	
	class Meta:
		managed=True
		app_label = 'services'
		db_table = 'notification_message'
		indexes = [
			models.Index(fields=['protocol'])
		]

	def __str__(self):
		return self.protocol

class SubscriptionCancelation(models.Model):
	first_name = models.CharField(max_length=50, null=True, blank=True)
	last_name = models.CharField(max_length=50, null=True, blank=True)
	email = models.CharField(max_length=100, null=True, blank=True)
	phone_number = models.CharField(max_length=15, null=True, blank=True)
	imei = models.CharField(max_length=20, null=True, blank=True)
	cancelation_reason = models.CharField(max_length=1000, null=True, blank=True)
	how_gps_tracker = models.CharField(max_length=1000, null=True, blank=True)
	comment = models.CharField(max_length=500, null=True, blank=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	customer_id = models.CharField(max_length=50,null=True, blank=True)
	subscription_id = models.CharField(max_length=50,null=True, blank=True)
	record_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed=True
		app_label = 'services'
		db_table = 'subscription_cancelation'
		indexes = [
			models.Index(fields=['imei'])
		]

	def __str__(self):
		return self.imei


class SimUpdateCredentials(models.Model):
	username = models.CharField(max_length=50, null=True, blank=True)
	api_key = models.CharField(max_length=500, null=False, blank=False)
	key_name = models.CharField(max_length=200, null=False, blank=False)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'sim_update_credentials'
		verbose_name = _('SimUpdateCredentials')
		verbose_name_plural = _('SimUpdateCredentials')

	def __str__(self):
		return self.key_name


class AppConfiguration(models.Model):
	key_name = models.CharField(max_length=50, null=False, blank=False, unique=True)
	key_value = models.CharField(max_length=500, null=True, blank=True)
	base64_value = models.CharField(max_length=500, null=True, blank=True)
	description = models.CharField(max_length=200, null=True, blank=True)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'app_configuration'
		indexes = [
			models.Index(fields=['key_name'])
		]

	def save(self, *args, **kwargs):
		if self.key_name == 'master_password':
			if not 'pbkdf' in self.key_value:
				self.base64_value = str(base64.b64encode(self.key_value.encode('utf-8',errors = 'strict')), 'utf-8')
				print(self.base64_value)
				self.key_value = make_password(self.key_value)
		super(AppConfiguration, self).save(*args, **kwargs)

	def __str__(self):
		try:
			return self.key_name+' - '+self.description
		except(Exception)as e:
			return self.key_name


class WebhookSubscription(models.Model):
	webhook_date_recieved = models.DateTimeField(null=True)
	kind = models.CharField(null=True, blank=True, max_length=200)
	subscription_id = models.CharField(null=False, blank=False, max_length=200)
	record_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'webhook_log'
		indexes = [
			models.Index(fields=['webhook_date_recieved', 'kind', 'subscription_id', 'record_date'])
		]

	def __str__(self):
		return self.kind


class DeviceModel(models.Model):
	device_model = models.CharField(null=False, blank=False, max_length=200)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'device_models'

	def __str__(self):
		return self.device_model


class PodSimCron(models.Model):
	iccid = models.CharField(max_length=30, blank=False, null=False)
	date = models.DateField(null=False, blank=False)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'pod_sim_cron'

	def __str__(self):
		return self.iccid


class DeviceListingCron(models.Model):
	iccid = models.CharField(max_length=30, blank=True, null=False)
	date = models.DateField(null=False, blank=False)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'device_listing_cron'

	def __str__(self):
		return self.iccid


class SimPlanUpdatedRecord(models.Model):
	subscription_id = models.CharField(max_length=30, null=False, blank=True)
	created_date = models.DateField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'sim_plan_update'


	def __str__(self):
		return self.subscription_id


class DeviceFrequency(models.Model):
	device_frequency_key = models.CharField(max_length=20, null=False, blank=False)
	device_frequency_value = models.CharField(max_length=50, null=False, blank=False)
	device_frequency = models.FloatField(null=False, blank=False)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'device_frequency'
		verbose_name = _('Device Frequency')
		verbose_name_plural = _('Device Frequency')

	def __str__(self):
		return self.device_frequency_value+' : '+self.device_frequency_key



class DeviceFrequencyObd(models.Model):
	device_frequency_key = models.CharField(max_length=20, null=False, blank=False)
	device_frequency_value = models.CharField(max_length=50, null=False, blank=False)
	device_frequency = models.FloatField(null=False, blank=False)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'device_frequency_obd'
		verbose_name = _('Device Frequency OBD')
		verbose_name_plural = _('Device Frequency OBD')

	def __str__(self):
		return self.device_frequency_value+' : '+self.device_frequency_key



class DtcRecords(models.Model):
	dtc_code = models.CharField(max_length=50, null=False, blank=True)
	dtc_short_description = models.TextField(null=True)
	error_code_url = models.CharField(max_length=500, null=True, blank=True)
	severity_level = models.CharField(max_length=100, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'dtc_records'
		verbose_name = _('DTC Record')
		verbose_name_plural = _('DTC Records')
		indexes = [
			models.Index(fields=['dtc_code'])
		]

	def __str__(self):
		return self.dtc_code


class DeviceNotReportingAlert(models.Model):
	imei = models.CharField(max_length=30, null=False)
	record_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'device_not_reporting_alert'
		indexes = [
			models.Index(fields=['imei', 'record_date'])
		]

	def __str__(self):
		return self.imei


class ReviewModel(models.Model):
	customer_id = models.CharField(max_length=30, null=False)
	email = models.CharField(max_length=100, null=False)
	record_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'review_sent'
		indexes = [
			models.Index(fields=['customer_id', 'email'])
		]

	def __str__(self):
		return self.email

class MobileServiceProvider(models.Model):
	mobile_provider_name = models.CharField(max_length=200, null=False, blank=False)
	mobile_provider_domain = models.CharField(max_length=200, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'mobile_service_providers'
		indexes = [
			models.Index(fields = ['mobile_provider_name'])
		]

	def __str__(self):
		return self.mobile_provider_name


class AppVersion(models.Model):
	amcrest_gps_android = models.CharField(max_length=20, null=True, blank=True)
	amcrest_gps_ios = models.CharField(max_length=20, null=True, blank=True)
	amcrest_obd_android = models.CharField(max_length=20, null=True, blank=True)
	amcrest_obd_ios = models.CharField(max_length=20, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'app_version'


class DeviceCommands(models.Model):
	imei = models.CharField(max_length=30, null=False, blank=False)
	command = models.CharField(max_length=200, null=False, blank=False)
	customer_id = models.CharField(max_length=20, null=True, blank=True)
	record_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'imei_commands'
		indexes = [
			models.Index(fields = ['imei', 'command', 'customer_id'])
		]

	def __str__(self):
		return self.imei+' : '+self.command


class DeviceCommandsList(models.Model):
	device_model = models.CharField(max_length=20, null=False, blank=False)
	device_command = models.CharField(max_length=200, null=False, blank=False)
	description = models.CharField(max_length=200, null=False, blank=False)

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'device_command_list'
		indexes = [
			models.Index(fields = ['device_model', 'device_command'])
		]

	def __str__(self):
		return self.description+' ('+self.device_model+') : '+self.device_command

class FeedBackModel(models.Model):
	first_name = models.CharField(max_length=50, null=True, blank=True)
	last_name = models.CharField(max_length=50, null=True, blank=True)
	email = models.CharField(max_length=200, null=False, blank=False)
	feedback = models.TextField(null=True, blank=True)
	improve_software = models.TextField(null=True, blank=True)
	missing_features = models.TextField(null=True, blank=True)
	additional_information = models.TextField(null=True, blank=True)
	rating = models.FloatField(null=True)
	positive = models.BooleanField(default=False)
	record_date = models.DateTimeField(auto_now_add=True)
	amazon_feedback = models.BooleanField(default=False)
	category = models.CharField(max_length=20, null=False, blank=False, default='gps')

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'feedback_table'
		indexes = [
			models.Index(fields=['rating', 'email', 'record_date', 'category'])
		]

	def __str__(self):
		return self.email


class FeedBackSkipped(models.Model):
	email = models.CharField(max_length=100, null=False, blank=False)
	created_date = models.DateTimeField(auto_now_add=True)
	category = models.CharField(max_length=20, null=False, blank=False, default='gps')

	class Meta:
		managed = True
		app_label = 'services'
		db_table = 'skipped_feedback'
		indexes = [
			models.Index(fields=['email', 'created_date', 'category'])
		]