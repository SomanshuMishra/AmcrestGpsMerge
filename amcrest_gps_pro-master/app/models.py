from django.db import models
from django.conf import settings

from django.contrib.auth import get_user_model

from django.db.models.signals import post_save as ps
from django.dispatch import receiver

from django.utils.translation import ugettext_lazy as _

from django_mysql.models import EnumField
from enumchoicefield import ChoiceEnum, EnumChoiceField


import base64
import json
import random
import datetime
import pytz
import _thread

# from app.serializers import SettingsSerializer
from services.models import *

from mongoengine import *
from mongoengine import signals

# from 

User = get_user_model()
default_time_zone = pytz.timezone("UTC")
# 864251020316075
# 864251020319244



class GoogleMapAPIKey(models.Model):
	key = models.TextField(null=False, blank=False)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'google_keys'


class Subscription(models.Model):
	gps_id = models.BigIntegerField(null=True)
	customer_id = models.BigIntegerField(null=True)
	subscription_id = models.CharField(max_length=100, null=True, blank=True)
	transaction_id = models.CharField(max_length=40, null=True, blank=True)
	subscription_status = models.CharField(max_length=100, null=True, blank=True)
	imei_no = models.CharField(max_length=25, null=True, blank=True)
	device_name = models.CharField(max_length=40, null=True, blank=True)
	device_model = models.CharField(max_length=50, null=True, blank=True)
	imei_iccid = models.CharField(max_length=100, null=True, blank=True)
	sim_status = models.BooleanField(null=True, default=False)
	ip_address = models.CharField(max_length=40, null=True, blank=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	firstBillingDate = models.DateField(null=True)
	nextBillingDate = models.DateField(null=True)
	order_id = models.CharField(max_length=50, null=True, blank=True)
	activated_plan_id = models.CharField(max_length=50, null=True, blank=True)
	activated_plan_description = models.CharField(max_length=200, null=True, blank=True)
	is_active = models.BooleanField(default=True, null=True)
	device_in_use = models.BooleanField(default=True, null=True)
	record_date = models.DateTimeField(auto_now_add=True)
	device_listing = models.BooleanField(default=True, null=True)
	# def __str__(self):
	# 		return self.customer_id	
	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'subscription'
		indexes = [
			models.Index(fields=['imei_no', 'customer_id', 'activated_plan_id', 'is_active', 'device_in_use', 'record_date']),
			models.Index(fields=['imei_no', 'sim_status']),
			models.Index(fields=['imei_no', 'customer_id']),
			models.Index(fields=['imei_no']),
			models.Index(fields=['imei_iccid']),
			models.Index(fields=['imei_no', 'device_listing', 'customer_id']),
			models.Index(fields=['device_model', 'device_listing', 'customer_id', 'device_in_use']),
			models.Index(fields=['is_active', 'customer_id']),
			models.Index(fields=['customer_id']),
			models.Index(fields=['subscription_id']),
		]
		
  


class ZoneGroup(models.Model):
	name = models.CharField(max_length=100)
	created_by = models.CharField(max_length=100)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'zone_group'
		indexes = [
			models.Index(fields=['created_by', 'created_on', 'name']),
			models.Index(fields=['created_by'])
		]


class Zones(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	coordinates = models.TextField(null=True, blank=True)
	type = models.CharField(max_length=20, null=False, blank=False)
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	status = models.BooleanField(default=True)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	zone_group = models.ForeignKey(ZoneGroup, null=True, on_delete=models.SET_NULL, related_name='zone_group')
	coordinates_tuple = models.TextField(null=True, blank=True)
	routes = models.TextField(null=True, blank=True)
	routes_tuple = models.TextField(null=True, blank=True)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'zones'
		indexes = [
			models.Index(fields=['customer_id', 'created_on',]),
			models.Index(fields=['customer_id']),
		]


	def make_tuple(self, coordinates):
		dlist = eval(coordinates)
		zone_list = []
		for z in dlist:
			zt = ()
			zt = zt + (float(z["lat"]),)
			zt = zt + (float(z["lng"]),)
			zone_list.append(zt)
		return json.dumps(zone_list)

	def save(self, *args, **kwargs):
		if self.coordinates:
			self.coordinates_tuple = self.make_tuple(self.coordinates)

		if self.routes:
			self.routes_tuple = self.make_tuple(self.routes)
		super(Zones, self).save(*args, **kwargs)



class ZoneAlert(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	zone = models.ForeignKey(Zones, related_name='zone_alert', on_delete=models.CASCADE, null=False)
	type = models.CharField(max_length=20, null=True, blank=True)
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	email_one = models.EmailField(null=True, blank=True)
	phone_one = models.CharField(null=True, blank=True, max_length=15)
	phone_one_mobile_carrier = models.CharField(max_length=50, null=True, blank=True)
	email_two = models.EmailField(null=True, blank=True)
	phone_two = models.CharField(null=True, blank=True, max_length=15)
	phone_two_mobile_carrier = models.CharField(max_length=50, null=True, blank=True)
	created_on = models.DateTimeField(auto_now_add=True)
	imei = models.CharField(max_length=20, null=True, blank=True)
	category = models.CharField(max_length=20)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'zone_alert'
		indexes = [
			models.Index(fields=['customer_id', 'created_on', 'name', 'zone', 'imei', 'category']),
			models.Index(fields=['customer_id',]),
		]




@receiver(ps, sender=Zones)
def update_zone_alert(sender, instance=None, created=False, **kwargs):
	zone_alerts = ZoneAlert.objects.filter(zone=instance.id).all()
	if zone_alerts:
		for zone_alert in zone_alerts:
			zone_alert.type = instance.type
			zone_alert.save()



class ZoneObd(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	type = models.CharField(max_length=20, null=False, blank=False)
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	latitude = models.CharField(max_length=30)
	longitude = models.CharField(max_length=30)
	radius = models.FloatField(null=False, blank=False)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'zone_obd'
		indexes = [
			models.Index(fields=['customer_id', 'created_on', 'name', 'type'])
		]

class ZoneAlertObd(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	zone = models.ForeignKey(ZoneObd, related_name='zone_alert_obd', on_delete=models.CASCADE, null=False)
	type = models.CharField(max_length=20, null=True, blank=True)
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	email_one = models.EmailField(null=True, blank=True)
	phone_one = models.CharField(null=True, blank=True, max_length=15)
	phone_one_mobile_carrier = models.CharField(max_length=50, null=True, blank=True)
	email_two = models.EmailField(null=True, blank=True)
	phone_two = models.CharField(null=True, blank=True, max_length=15)
	phone_two_mobile_carrier = models.CharField(max_length=50, null=True, blank=True)
	created_on = models.DateTimeField(auto_now_add=True)
	imei = models.CharField(max_length=20, null=True, blank=True)
	status = models.BooleanField(default=False)
	zone_device_id = models.IntegerField(null=False)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'zone_alert_obd'
		indexes = [
			models.Index(fields=['customer_id', 'created_on', 'name', 'imei', 'type', 'zone']),
			models.Index(fields=['customer_id','zone']),
			models.Index(fields=['zone']),
			models.Index(fields=['customer_id']),
		]



class NoticationSender(models.Model):
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	android = models.CharField(max_length=200, null=True, blank=True)
	ios = models.CharField(max_length=200, null=True, blank=True)
	website = models.CharField(max_length=200, null=True, blank=True)
	category = models.CharField(max_length=20, null=True, blank=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'notification_sender'
		indexes = [
			models.Index(fields=['customer_id'])
		]



#-------------------------Events


class Odometere(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	distance = models.FloatField(null=True)
	record_date = models.DateField(auto_now_add=True)
	record_date_timezone = models.DateField(null=True)
	customer_id = models.BigIntegerField(null=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'odometere'
		indexes = [
			models.Index(fields=['imei', 'record_date_timezone', 'record_date', 'customer_id'])
		]

	def save(self, *args, **kwargs):
		self.distance = round(self.distance, 2)
		super(Odometere, self).save(*args, **kwargs)


class TripEvents(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	type = models.CharField(max_length=12, null=False, blank=False)
	location = models.CharField(max_length=500, null=True, blank=True)
	date = models.DateField(null=True)
	time = models.TimeField(null=True)
	record_date = models.DateField(null=True)
	customer_id = models.BigIntegerField(null=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'trip_events'
		indexes = [
			models.Index(fields=['imei', 'type', 'date', 'time', 'record_date', 'customer_id'])
		]


class VoltageModel(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	min_voltage = models.FloatField(null=True)
	max_voltage = models.FloatField(null=True)
	avg_voltage = models.FloatField(null=True)
	record_date = models.DateField(null=True)
	customer_id = models.BigIntegerField(null=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'voltage'
		indexes = [
			models.Index(fields=['imei', 'record_date', 'min_voltage', 'max_voltage', 'customer_id'])
		]


class HarshBehaviourEvent(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	harsh_type = models.CharField(max_length=100, null=True, blank=True)
	record_date = models.DateField(null=True)
	record_time = models.TimeField(null=True)
	customer_id = models.BigIntegerField(null=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'harsh_behaviour_events'
		indexes = [
			models.Index(fields=['imei', 'record_date', 'record_time', 'customer_id'])
		]

class FuelEconomy(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	fuel_economy = models.FloatField(null=True)
	record_date = models.DateField(null=True)
	customer_id = models.BigIntegerField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'fuel_economy'
		indexes = [
			models.Index(fields=['imei', 'record_date', 'fuel_economy'])
		]



class Emission(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	emission = models.FloatField(null=True)
	record_date = models.DateField(null=True)
	customer_id = models.BigIntegerField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'emission'
		indexes = [
			models.Index(fields=['imei', 'record_date', 'emission', 'customer_id'])
		]


class FuelConsumption(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	consumption = models.FloatField(null=True)
	record_date = models.DateField(null=True)
	customer_id = models.BigIntegerField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'fuel_consumption'
		indexes = [
			models.Index(fields=['imei', 'record_date', 'consumption', 'customer_id'])
		]


class DriverScore(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False)
	driver_score = models.FloatField(null=True)
	record_date = models.DateField(null=True)
	customer_id = models.BigIntegerField(null=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'driver_score'
		indexes = [
			models.Index(fields=['imei', 'record_date', 'driver_score'])
		]


class DtcEvents(models.Model):
	imei = models.CharField(max_length=25, null=False, blank=False)
	customer_id = models.CharField(max_length=20, null=True, blank=True)
	record_date = models.DateField(null=True)
	record_time = models.TimeField(null=True)
	protocol = models.CharField(max_length=12, blank=True, null=True)
	dtc_code = models.CharField(max_length=50, null=False, blank=True)
	dtc_short_description = models.TextField(null=True)
	error_code_url = models.CharField(max_length=500, null=True, blank=True)
	severity_level = models.CharField(max_length=100, null=True, blank=True)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'dtc_events'
		indexes = [
			models.Index(fields=['imei', 'customer_id', 'record_date', 'dtc_code'])
		]


class OBDDtcEvents(models.Model):
	imei = models.CharField(max_length=25, null=False, blank=False)
	customer_id = models.CharField(max_length=20, null=True, blank=True)
	record_date = models.DateField(null=True)
	record_time = models.TimeField(null=True)
	protocol = models.CharField(max_length=12, blank=True, null=True)
	warning_code = models.CharField(max_length=40, blank=True, null=True)
	warning_value = models.CharField(max_length=40, blank=True, null=True)
	warning_details = models.CharField(max_length=240, blank=True, null=True)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'obd_dtc_events'
		indexes = [
			models.Index(fields=['imei', 'customer_id', 'record_date', 'warning_code'])
		]


################-------------------------TRIPS----------------------------#######################
class TripEndRecord(models.Model):
	imei = models.CharField(max_length=30)
	details = models.TextField()
	protocol = models.CharField(max_length=20)
	record_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'trip_end_record'
		indexes = [
			models.Index(fields=['imei', 'protocol', 'record_date'])
		]


class BufferRecord(Document):
	imei = StringField(null=False)
	details = DictField(null=True)

	meta = {
		'auto_create_index':False,
		'indexes':[
			{
				'fields':['+imei', '+details']
			}
		]
	}

class GlBufferRecord(Document):
	imei = StringField(null=False)
	details = DictField(null=True)

	meta = {
		'auto_create_index':False,
		'indexes':[
			{
				'fields':['+imei', '+details']
			}
		]
	}



class TripCalculationData(models.Model):
    imei = models.CharField(max_length=20, null=False, blank=False)
    _details = models.TextField(null=True, blank=True, db_column='details')

    def set_data(self, details):
    	self._details = base64.encodestring(details)

    def get_data(self):
    	return base64.decodestring(self._details)

    details = property(get_data, set_data)

    class Meta:
    	managed=True
    	app_label = 'listener'
    	db_table = 'trip_calculation_data'
    	indexes = [
			models.Index(fields=['imei'])
			]


class UserTrip(Document):
	measure_id = IntField(unique=True)
	trip_log = ListField()
	imei = StringField()
	record_date = DateTimeField(default=datetime.datetime.now)
	record_date_timezone = DateTimeField()
	driver_id = StringField()
	customer_id = StringField()
	start_time = DateTimeField(null=True)
	end_time = DateTimeField(null=True)

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['-imei', '-record_date_timezone']
			},
			{
				'fields': ['+imei', '-record_date_timezone']
			},
			{
				'fields': ['+imei', '+record_date_timezone']
			},
			{
				'fields': ['+imei', '+customer_id', '+record_date_timezone']
			},
			{
				'fields': ['+imei', '+customer_id', '-record_date_timezone']
			},
			{
				'fields': ['+imei']
			},
			{
				'fields': ['+imei', '+customer_id']
			},
			{
				'fields': ['+customer_id']
			},
			{
				'fields': ['+record_date_timezone']
			},
			{
				'fields': ['-record_date_timezone']
			}
		]
       }

	@classmethod
	def post_save(cls, sender, document, **kwargs):
		from app.events.trips import trip_event_module
		if kwargs['created']:
			try:
				random_number = str(random.randint(0,100000,))+''+str(datetime.datetime.now().year)[2:]+''+str(datetime.datetime.now().day)+''+str(datetime.datetime.now().month)+''+str(datetime.datetime.now().hour)+''+str(datetime.datetime.now().minute)+''+str(datetime.datetime.now().second)
				document.measure_id = str(random_number)
				document.save()
				# print(document.measure_id)
			except(Exception)as e:
				document.measure_id = str(random.randint(0,1000000,))+''+str(random.randint(0,2000000,))
				document.save()
				print(e)
				pass



signals.post_save.connect(UserTrip.post_save, sender=UserTrip)
# signals.post_save.connect(FeaturedUserTrip.post_save, sender=FeaturedUserTrip)




class UserObdTrip(Document):
	measure_id = IntField(unique=True)
	trip_log = ListField()
	imei = StringField()
	record_date = DateTimeField(default=datetime.datetime.now)
	record_date_timezone = DateTimeField()
	driver_id = StringField()
	customer_id = StringField()
	start_time = DateTimeField(null=True)
	end_time = DateTimeField(null=True)

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['-imei', '-record_date_timezone']
			},
			{
				'fields': ['+imei', '-record_date_timezone']
			},
			{
				'fields': ['+imei', '+record_date_timezone']
			},
			{
				'fields': ['+imei', '+customer_id', '+record_date_timezone']
			},
			{
				'fields': ['+imei', '+customer_id', '-record_date_timezone']
			},
			{
				'fields': ['+imei']
			},
			{
				'fields': ['+imei', '+customer_id']
			},
			{
				'fields': ['+customer_id']
			},
			{
				'fields': ['+record_date_timezone']
			},
			{
				'fields': ['-record_date_timezone']
			}
		]
       }

	@classmethod
	def post_save(cls, sender, document, **kwargs):
		from app.events.trips import trip_event_module
		if kwargs['created']:
			try:
				random_number = str(random.randint(0,100000,))+''+str(datetime.datetime.now().year)[2:]+''+str(datetime.datetime.now().day)+''+str(datetime.datetime.now().month)+''+str(datetime.datetime.now().hour)+''+str(datetime.datetime.now().minute)+''+str(datetime.datetime.now().second)
				document.measure_id = str(random_number)
				document.save()
				# print(document.measure_id)
			except(Exception)as e:
				document.measure_id = str(random.randint(0,1000000,))+''+str(random.randint(0,2000000,))
				document.save()
				print(e)
				pass



signals.post_save.connect(UserObdTrip.post_save, sender=UserObdTrip)

class TripsMesurement(Document):
	measure_id = IntField()
	total_distance = ListField()
	total_time = ListField()
	customer_id = StringField()

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['+measure_id', '+customer_id']
			}
		]
       }


class TripsObdMesurement(Document):
	measure_id = IntField()
	total_distance = ListField()
	total_time = ListField()
	customer_id = StringField()

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['+measure_id', '+customer_id']
			}
		]
       }




#---------------Backup User Trip
class UserTripBackup(Document):
	measure_id = IntField(unique=True)
	trip_log = ListField()
	imei = StringField()
	record_date = DateTimeField()
	record_date_timezone = DateTimeField()
	driver_id = StringField()
	customer_id = StringField()
	start_time = DateTimeField(null=True)
	end_time = DateTimeField(null=True)

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['-imei', '-record_date_timezone']
			},
			{
				'fields': ['+imei', '-record_date_timezone']
			},
			{
				'fields': ['+imei', '+record_date_timezone']
			},
			{
				'fields': ['+imei', '+customer_id', '+record_date_timezone']
			},
			{
				'fields': ['+imei', '+customer_id', '-record_date_timezone']
			},
			{
				'fields': ['+imei']
			},
			{
				'fields': ['+imei', '+customer_id']
			},
			{
				'fields': ['+customer_id']
			},
			{
				'fields': ['+record_date_timezone']
			},
			{
				'fields': ['-record_date_timezone']
			}
		]
       }


class TripsMesurementBackup(Document):
	measure_id = IntField()
	total_distance = ListField()
	total_time = ListField()
	customer_id = StringField(null=True)

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['+measure_id', '+customer_id']
			}
		]
       }

#-------------------------------Reports----------------------
class Reports(Document):
	imei = StringField()
	device_name = StringField(null=True)
	alert_name = StringField(null=True)
	event_type = StringField(null=True)
	battery_percentage = StringField(null=True)
	report_time = DateTimeField(default=datetime.datetime.now)
	location = StringField(null=True)
	longitude = StringField(null=True)
	latitude = StringField(null=True)
	speed = StringField(null=True)
	type = StringField(null=True)
	notification_sent = BooleanField(default=False)
	customer_id = StringField(null=True)
	speed_status = BooleanField(default=False)
	battery_status = BooleanField(default=False)
	record_date_timezone = DateTimeField()

	meta = {
		'auto_create_index':False,
		'indexes': [
			{
				'fields': ['+imei', '+event_type', '+type', '+customer_id', '+record_date_timezone', '+notification_sent', '+speed_status', '+battery_status', '+report_time', '+alert_name']
			},
			{
				'fields': ['+imei']
			},
			{
				'fields': ['+customer_id']
			},
			{
				'fields': ['+record_date_timezone']
			},
			{
				'fields': ['+record_date_timezone', '+imei', '+customer_id']
			},
			{
				'fields': ['+record_date_timezone', '+imei']
			},
			{
				'fields': ['-record_date_timezone', '-imei']
			},
			{
				'fields': ['-record_date_timezone']
			},
			{
				'fields': ['+type']
			},
			{
				'fields': ['+type', '+imei']
			}
		]
       }

	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
			if user:
				if user.time_zone:
					return user.time_zone
		return 'UTC'

	def get_time_timezone(self, imei, date):
		time_zone = self.get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%Y-%m-%d %H:%M:%S")
		return date_to_be_send

	def get_customer_id(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			return str(sub.customer_id)
		return None

	def save(self, *args, **kwargs):
		if not self.record_date_timezone:
			self.record_date_timezone = self.get_time_timezone(self.imei, self.report_time)
		self.customer_id = self.get_customer_id(self.imei)
		super(Reports, self).save(*args, **kwargs)


class ZoneNotificationChecker(Document):
	imei = StringField()
	report_time = DateTimeField(default=datetime.datetime.now)
	event_type = StringField(null=True)
	customer_id = StringField(null=True)
	zone = IntField(null=True)
	zone_alert = IntField(null=True)

	meta = {
		'auto_create_index':False,
		'indexes': [
			{
				'fields': ['+imei', '+event_type', '+customer_id', '+zone', '+zone_alert']
			},
			{
				'fields': ['+imei', '+event_type', '+zone', '+zone_alert']
			}
		]
       }
	
	def get_customer_id(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		return str(sub.customer_id)

	def save(self, *args, **kwargs):
		self.customer_id = self.get_customer_id(self.imei)
		super(ZoneNotificationChecker, self).save(*args, **kwargs)


class Notifications(Document):
	customer_id = StringField()
	title = StringField(null=True)
	body = StringField(null=True)
	imei = StringField()
	type = StringField()
	record_time = DateTimeField(default=datetime.datetime.now)
	record_date_timezone = DateTimeField()
	longitude = StringField(null=True)
	latitude = StringField(null=True)
	alert_name = StringField(null=True)
	event = StringField(null=True)
	battery_percentage = StringField(null=True)
	location = StringField(null=True)
	speed = StringField(null=True)

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['+imei', '+customer_id', '+record_date_timezone', '+type', '+record_time', '+alert_name', '+event', '+speed']
			},
			{
				'fields': ['+imei', '+customer_id', '+record_date_timezone', '+type']
			},
			{
				'fields': ['+imei']
			},
			{
				'fields': ['+customer_id']
			},
			{
				'fields': ['+record_date_timezone']
			},
			{
				'fields': ['+type']
			},
			{
				'fields': ['-record_date_timezone']
			},
			{
				'fields': ['+imei','+customer_id']
			},
			{
				'fields': ['+imei','+customer_id', '+type']
			}
		]
       }



class NotificationsBackup(Document):
	customer_id = StringField()
	title = StringField(null=True)
	body = StringField(null=True)
	imei = StringField()
	type = StringField()
	record_time = DateTimeField(default=datetime.datetime.now)
	record_date_timezone = DateTimeField()
	longitude = StringField(null=True)
	latitude = StringField(null=True)
	alert_name = StringField(null=True)
	event = StringField(null=True)
	battery_percentage = StringField(null=True)
	location = StringField(null=True)
	speed = StringField(null=True)

	meta = {
		'auto_create_index':True,
		'indexes': [
			{
				'fields': ['+imei', '+customer_id', '+record_date_timezone', '+type', '+record_time', '+alert_name', '+event', '+speed']
			},
			{
				'fields': ['+imei', '+customer_id', '+record_date_timezone', '+type']
			},
			{
				'fields': ['+imei']
			},
			{
				'fields': ['+customer_id']
			},
			{
				'fields': ['+record_date_timezone']
			},
			{
				'fields': ['+type']
			},
			{
				'fields': ['-record_date_timezone']
			},
			{
				'fields': ['+imei','+customer_id']
			},
			{
				'fields': ['+imei','+customer_id', '+type']
			}
		]
       }


class SmsLog(Document):
	customer_id = StringField()
	imei = StringField(null=True)
	message = StringField(null=True)
	record_time = DateTimeField(default=datetime.datetime.now)

	meta = {
		'auto_create_index':False,
		'indexes': [
			{
				'fields': ['+imei', '+customer_id', '+record_time']
			}
		]
       }

class SmsEmailCount(models.Model):
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	email_count = models.IntegerField(null=True)
	sms_count = models.IntegerField(null=True)
	record_date = models.DateField(auto_now_add=True)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'sms_email_count'
		indexes = [
			models.Index(fields=['customer_id', 'record_date'])
		]
#-------------------------------Reports----------------------
class Location(Document):
	longitude = StringField()
	latitude = StringField()
	location_name = StringField()

	meta = {
		'auto_create_index':False,
		'indexes': [
			{
				'fields': ['+longitude', '+latitude', '+location_name']
			}
		]
       }

#---------------------map
class MapSettings(models.Model):
	customer_id = models.CharField(max_length=50, null=True, blank=True, unique=True)
	map_type = models.CharField(max_length=50, null=True, blank=True, default='standard')
	traffic = models.BooleanField(default=True)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'map_settings'
		indexes = [
			models.Index(fields=['customer_id'])
		]

# -----Settings

class SettingsModel(models.Model):
	imei = models.CharField(max_length=35, null=False, blank=False, unique=True)
	customer_id = models.CharField(max_length=50, null=True, blank=True)
	device_name = models.CharField(max_length=100, null=False, blank=False)
	vehicle_type = models.CharField(max_length=50, blank=False, default='car')
	vehicle_color = models.CharField(max_length=50, blank=False, default='grey1')
	device_reporting_frequency = models.CharField(max_length=20, null=True, blank=True)
	device_reporting_frequency_desc = models.CharField(max_length=100, null=True, blank=True)
	trip_end_timer = models.IntegerField(default=10, null=True)
	battery_low_limit = models.IntegerField(default=15, null=True)
	device_frequency_value = models.FloatField(null=True)
	speed_limit = models.FloatField(null=True, default=80)

	show_speed = models.BooleanField(default=True, null=True)
	show_engine_rpm = models.BooleanField(default=True, null=True)
	show_mileage = models.BooleanField(default=True, null=True)
	show_fuel_consumption = models.BooleanField(default=True, null=True)
	show_engine_temp = models.BooleanField(default=True, null=True)
	show_voltage = models.BooleanField(default=True, null=True)
	show_engine_load = models.BooleanField(default=True, null=True)
	show_throttle_position = models.BooleanField(default=True, null=True)
	show_location = models.BooleanField(default=True, null=True)
	show_fuel_level = models.BooleanField(default=True, null=True)

	email = models.CharField(max_length=1000, null=True, blank=True)
	phone = models.CharField(max_length=1000, null=True, blank=True)
	mobile_carrier = models.CharField(max_length=50, null=True, blank=True)
	secondary_phone = models.CharField(max_length=15, null=True, blank=True)
	secondary_mobile_carrier = models.CharField(max_length=50, null=True, blank=True)

	trip_notification_global = models.BooleanField(default=True)
	trip_notification = models.BooleanField(default=False)
	trip_email = models.BooleanField(default=False)
	trip_sms = models.BooleanField(default=False)

	engine_notification_global = models.BooleanField(default=True)
	engine_notification = models.BooleanField(default=True)
	engine_email = models.BooleanField(default=False)
	engine_sms = models.BooleanField(default=False)

	speed_notification_global = models.BooleanField(default=True)
	speed_notification = models.BooleanField(default=True)
	speed_sms = models.BooleanField(default=False)
	speed_email = models.BooleanField(default=False)

	zone_alert_notification = models.BooleanField(default=True)

	harsh_notification_global = models.BooleanField(default=True)
	harshbraking_notification = models.BooleanField(default=True)
	harshbraking_sms = models.BooleanField(default=False)
	harshbraking_email = models.BooleanField(default=False)
	harshturning_notification = models.BooleanField(default=True)
	harshturning_sms = models.BooleanField(default=False)
	harshturning_email = models.BooleanField(default=False)
	harshacceleration_notification = models.BooleanField(default=True)
	harshacceleration_email = models.BooleanField(default=False)
	harshacceleration_sms = models.BooleanField(default=False)

	sos_notification_global = models.BooleanField(default=True)
	sos_notification = models.BooleanField(default=True)
	sos_sms = models.BooleanField(default=False)
	sos_email = models.BooleanField(default=False)

	charging_notification_global = models.BooleanField(default=True)
	charging_notification = models.BooleanField(default=True)
	charging_sms = models.BooleanField(default=False)
	charging_email = models.BooleanField(default=False)

	power_notification_global = models.BooleanField(default=True)
	power_notification = models.BooleanField(default=True)
	power_sms = models.BooleanField(default=False)
	power_email = models.BooleanField(default=False)

	show_battery = models.BooleanField(default=True)

	battery_notification_global = models.BooleanField(default=True)
	battery_notification = models.BooleanField(default=True)
	battery_email = models.BooleanField(default=False)
	battery_sms = models.BooleanField(default=False)

	attach_dettach_notification_global = models.BooleanField(default=True)
	attach_dettach_notification = models.BooleanField(default=True)
	attach_dettach_email = models.BooleanField(default=False)
	attach_dettach_sms = models.BooleanField(default=False)

	trip_sensor = models.BooleanField(default=False)
	trip_coordinate = models.BooleanField(default=True)

	global_sms = models.BooleanField(default=True)
	global_email = models.BooleanField(default=True)
	global_notification = models.BooleanField(default=True)

	tow_notification_global = models.BooleanField(default=True)
	tow_notification = models.BooleanField(default=True)
	tow_email = models.BooleanField(default=False)
	tow_sms = models.BooleanField(default=False)

	warning_notification_global = models.BooleanField(default=False)
	warning_notification = models.BooleanField(default=False)
	warning_email = models.BooleanField(default=False)
	warning_sms = models.BooleanField(default=False)

	fuel_capacity = models.FloatField(null=True)
	fuel_capacity_unit = models.CharField(max_length=20, default='gallon')

	def __str__(self):
		return self.imei

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'settings'
		indexes = [
			models.Index(fields=['imei', 'customer_id']),
			models.Index(fields=['imei']),
		]


	def change_device_name(self, imei, device_name):
		subscription = Subscription.objects.filter(imei_no=imei).last()
		if subscription:
			subscription.device_name = device_name
			subscription.save()

	def get_device_frequency(self, frequency):
		
		device_frq = DeviceFrequency.objects.filter(device_frequency_key=frequency).first()
		if device_frq:
			return device_frq.device_frequency
		return 5

	def get_device_frequency_info(self, frequency):
		device_frq = DeviceFrequency.objects.filter(device_frequency_key=frequency).first()
		if device_frq:
			return device_frq.device_frequency, device_frq.device_frequency_value
		else:
			device_frq = DeviceFrequencyObd.objects.filter(device_frequency_key=frequency).first()
			if device_frq:
				return device_frq.device_frequency, device_frq.device_frequency_value
		return 1, '1 min device frequency (10-14 days battery life)'

	def save(self, *args, **kwargs):
		self.change_device_name(self.imei, self.device_name)
		value, desc = self.get_device_frequency_info(self.device_reporting_frequency)
		self.device_frequency_value = value
		self.device_reporting_frequency_desc = desc
		super(SettingsModel, self).save(*args, **kwargs)



def get_device_frequency_info(activated_plan_id):
	ser = ServicePlan.objects.filter(service_plan_id=activated_plan_id).last()
	if ser:
		return ser.base_device_frequency
	else:
		ser = ServicePlanObd.objects.filter(service_plan_id=activated_plan_id).last()
		if ser:
			return ser.base_device_frequency
	return '60_sec'

@receiver(ps, sender=Subscription)
def create_settings(sender, instance=None, created=False, **kwargs):
	if created:
		device = Subscription.objects.filter(imei_no=instance.imei_no).last()
		if device:
			user = User.objects.filter(customer_id=device.customer_id, subuser=False).first()
			if user:
				email = user.emailing_address
				phone = user.phone_number
				mobile_carrier = user.mobile_carrier
			else:
				email = None
				phone = None
				mobile_carrier = None
				# activated_plan_id


			check_setting = SettingsModel.objects.filter(imei=device.imei_no).last()
			if not check_setting:
				if device.activated_plan_id == '30_second_interval':
					device_reporting_frequency = '30_sec'
					device_reporting_frequency_desc = '30 seconds device frequency'
				elif device.activated_plan_id == 'monthly':
					device_reporting_frequency = '60_sec'
					device_reporting_frequency_desc = '60 seconds device frequency'
				else:
					device_reporting_frequency = '60_sec'
					device_reporting_frequency_desc = '60 seconds device frequency'


				device_settings = SettingsModel(
						imei = device.imei_no,
						customer_id = device.customer_id,
						device_name = device.device_name,
						email = email,
						phone = phone,
						mobile_carrier = mobile_carrier,
						device_reporting_frequency = get_device_frequency_info(device.activated_plan_id)

					)
				device_settings.save()
			else:
				check_setting.device_reporting_frequency = get_device_frequency_info(device.activated_plan_id)
				check_setting.save()
	# else:
	# 	device = Subscription.objects.filter(imei_no=instance.imei_no).last()
	# 	if device:
	# 		check_setting = SettingsModel.objects.filter(imei=instance.imei_no).last()
	# 		if check_setting:
	# 			check_setting.device_reporting_frequency = get_device_frequency_info(device.activated_plan_id)
	# 			check_setting.save()




class IndividualTracking(models.Model):
	imei = models.CharField(max_length=20, null=False, blank=False, unique=True)
	key = models.CharField(max_length=254, null=False, blank=False, unique=True)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'individual_tracking'
		indexes = [
			models.Index(fields=['imei', 'key'])
		]



class TripCalculationGLCron(Document):
    imei = StringField(null=False)
    details = DictField(null=False)
    protocol = StringField(null=False)
    mileage = FloatField(null=False)
    send_time = LongField(null=False)

    meta = {
		'auto_create_index':False,
		'indexes': [
			{
				'fields': ['+imei', '+protocol', '+mileage', '+send_time', '+details']
			}
		]
       }


class TripCalculationObdCron(Document):
    imei = StringField(null=False)
    details = DictField(null=False)
    protocol = StringField(null=False)
    mileage = FloatField(null=False)
    send_time = LongField(null=False)

    meta = {
		'auto_create_index':False,
		'indexes': [
			{
				'fields': ['+imei', '+protocol', '+mileage', '+send_time', '+details']
			}
		]
       }


class FreeTrialModel(models.Model):
	imei = models.CharField(max_length=30, null=False, blank=False)
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	free_trial_month = models.IntegerField(null=False)
	record_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.imei +'-'+str(self.free_trial_month)

class GpsIdealTime(models.Model):
	imei = models.CharField(max_length=30, null=False, blank=False)
	ideal_time = models.CharField(max_length=5, null=False, blank=False)
	from_send_time = models.CharField(max_length=30, null=False, blank=False)
	to_send_time = models.CharField(max_length=30, null=False, blank=False)
	start_record = models.TextField(null=True, blank=True)
	end_record = models.TextField(null=True, blank=True)
	created_on = models.DateTimeField(auto_now_add=True)
	record_date_timezone = models.DateField(null=True)

	def __str__(self):
		return self.imei +'-'+str(self.ideal_time)


	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'gps_ideal_time'
		indexes = [
			models.Index(fields=['imei']),
			models.Index(fields=['imei', 'created_on']),
			models.Index(fields=['imei', 'record_date_timezone']),
		]


class BatteryDrain(models.Model):
	imei = models.CharField(max_length=30, null=False, blank=False)
	mileage = models.CharField(max_length=10, null=False, blank=False)
	time_spent = models.CharField(max_length=10, null=False, blank=False)
	battery = models.CharField(max_length=10, null=False, blank=False)
	date = models.DateField(null=False)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		managed=True
		app_label = 'app'
		db_table = 'battery_drain'
		indexes = [
			models.Index(fields=['imei']),
			models.Index(fields=['imei', 'created_on']),
			models.Index(fields=['imei', 'date']),
		]


class FuelLevelTracker(models.Model):
	imei = models.CharField(max_length=30, null=False, blank=False)
	start_mileage = models.FloatField(null=True)
	start_fuel_level = models.FloatField(null=True)
	end_mileage = models.FloatField(null=True)
	end_fuel_level = models.FloatField(null=True)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	class Meta:
		managed =True
		app_label = 'app'
		db_table = 'fuel_level_tracker'
		indexes = [
			models.Index(fields=['imei']),
		]