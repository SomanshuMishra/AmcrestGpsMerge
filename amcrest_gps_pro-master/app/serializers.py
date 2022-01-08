from rest_framework import serializers
from app.models import *
from listener.models import *
from django.conf import settings

from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework_mongoengine.serializers import *
# from rest_framework_mongoengine.serializers import *



class SubscriptionSerializer(serializers.ModelSerializer):
	gps_id = serializers.IntegerField(required=False, allow_null=True)
	customer_id = serializers.IntegerField(required=False, allow_null=True)
	subscription_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	transaction_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	subscription_status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	imei_no = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	device_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	device_model = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	imei_iccid = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	sim_status = serializers.BooleanField(required=False, allow_null=True)
	ip_address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	start_date = serializers.DateField(required=False, allow_null=True)
	end_date = serializers.DateField(required=False, allow_null=True)
	firstBillingDate = serializers.DateField(required=False, allow_null=True)
	nextBillingDate = serializers.DateField(required=False, allow_null=True)
	activated_plan_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	activated_plan_description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	is_active = serializers.BooleanField(required=False, allow_null=True)
	device_in_use = serializers.BooleanField(required=False, allow_null=True)
	device_listing = serializers.BooleanField(required=False, allow_null=True)

	class Meta:
		model = Subscription
		fields = '__all__'



class DeviceListSerializer(serializers.ModelSerializer):

	class Meta:
		model = Subscription
		fields = ['gps_id', 'customer_id', 'imei_no', 'device_name', 'id', 'device_listing', 'device_model']



class ZoneGroupWriteSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	created_by = serializers.CharField(required=True, allow_null=False, allow_blank=False)

	class Meta:
		model = ZoneGroup
		fields = '__all__'


class ZoneGroupUpdateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=False, allow_null=False, allow_blank=False)
	created_by = serializers.CharField(required=False, allow_null=False, allow_blank=False)

	class Meta:
		model = ZoneGroup
		fields = '__all__'



class ZoneGroupReadSerializer(serializers.ModelSerializer):

	class Meta:
		model = ZoneGroup
		fields = ['id', 'name', 'created_on', 'updated_on']


class ZoneWriteSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	coordinates = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	type = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	customer_id = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	status = serializers.BooleanField(required=False)
	created_on = serializers.DateTimeField(required=False)
	updated_on = serializers.DateTimeField(required=False)
	coordinates_tuple = serializers.CharField(required=False)
	routes = serializers.CharField(required=False)
	routes_tuple = serializers.CharField(required=False)

	class Meta:
		model = Zones
		fields = '__all__'


class ZoneLoaderSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(required=True)
	name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	coordinates = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	type = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	customer_id = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	status = serializers.BooleanField(required=False)
	created_on = serializers.DateTimeField(required=False)
	updated_on = serializers.DateTimeField(required=False)
	coordinates_tuple = serializers.CharField(required=False)
	routes = serializers.CharField(required=False)
	routes_tuple = serializers.CharField(required=False)

	class Meta:
		model = Zones
		fields = '__all__'

class ZoneReadSerializer(serializers.ModelSerializer):
	class Meta:
		model = Zones
		fields = ['id', 'name', 'coordinates', 'type', 'created_on', 'updated_on', 'status', 'zone_group', 'routes', 'routes_tuple']

class ZoneUpdateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	coordinates = serializers.CharField(required=False, allow_null=False, allow_blank=False)
	type = serializers.CharField(required=False, allow_null=False, allow_blank=False)
	customer_id = serializers.CharField(required=False, allow_null=False, allow_blank=False)
	status = serializers.BooleanField(required=False)
	created_on = serializers.DateTimeField(required=False)
	updated_on = serializers.DateTimeField(required=False)
	routes = serializers.CharField(required=False)
	routes_tuple = serializers.CharField(required=False)

	class Meta:
		model = Zones
		fields = '__all__'




class ZoneAlertSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	# zone = serializers.IntegerField(required=True)
	type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	customer_id = serializers.IntegerField(required=True, allow_null=False)
	email_one = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
	phone_one = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	email_two = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
	phone_two = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	created_on = serializers.DateTimeField(required=False)
	imei = serializers.CharField(required=False)

	class Meta:
		model = ZoneAlert
		fields = '__all__'

class ZoneAlertUpdateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	email_one = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
	phone_one = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	email_two = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
	phone_two = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	customer_id = serializers.IntegerField(required=False, read_only=True)

	class Meta:
		model = ZoneAlert
		fields = ['id', 'name', 'phone_two', 'phone_one', 'email_one', 'email_two', 'customer_id', 'imei', 'phone_one_mobile_carrier', 'phone_two_mobile_carrier']


#------ Zone brief Read Serializer
class ZoneBriefReadSerializer(serializers.ModelSerializer):
	class Meta:
		model = Zones
		fields = ['id', 'name', 'type', 'created_on', 'updated_on', 'status', 'zone_group']



class ZoneAlertReadSerializer(serializers.ModelSerializer):
	# zone = ZoneBriefReadSerializer()
	class Meta:
		model = ZoneAlert
		fields = ['id', 'name', 'phone_two', 'phone_one', 'email_one', 'email_two', 'created_on', 'type', 'customer_id', 'zone', 'imei', 'phone_one_mobile_carrier', 'phone_two_mobile_carrier']


class NotificationSenderSerializer(serializers.ModelSerializer):
	customer_id = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	android = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	ios = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	website = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	category = serializers.CharField(required=True, allow_null=False)
	class Meta:
		model = NoticationSender
		fields = '__all__'



###################------------OBD ZONE

class ZoneObdSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	type = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	customer_id = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	latitude = serializers.FloatField(required=True, allow_null=False)
	longitude = serializers.FloatField(required=True, allow_null=False)

	class Meta:
		model = ZoneObd
		fields = '__all__'


class ObdZoneUpdateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	type = serializers.CharField(required=False, allow_null=False, allow_blank=False)
	customer_id = serializers.CharField(required=False, allow_null=False, allow_blank=False)
	latitude = serializers.FloatField(required=False, allow_null=False)
	longitude = serializers.FloatField(required=False, allow_null=False)

	class Meta:
		model = ZoneObd
		fields = '__all__'


class ZoneAlertObdSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
	class Meta:
		model = ZoneAlertObd
		fields = '__all__'


class ZoneAlertObdUpdateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	email_one = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
	phone_one = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	email_two = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
	phone_two = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	customer_id = serializers.IntegerField(required=False, read_only=True)

	class Meta:
		model = ZoneAlertObd
		fields = ['id', 'name', 'phone_two', 'phone_one', 'email_one', 'email_two', 'customer_id', 'imei', 'phone_one_mobile_carrier', 'phone_two_mobile_carrier']


###################-------------------------


class TripCalculationDataSerializer(serializers.ModelSerializer):
	imei = serializers.CharField(required=True, allow_null=False)
	_details = serializers.CharField(allow_null=False, allow_blank=False, required=True)

	class Meta:
		model = TripCalculationData
		fields = '__all__'


class DeviceObdMarkersSerializer(serializers.ModelSerializer):

    class Meta:
    	model = ObdMarkers
    	fields = ['engine_rpm', 'engine_coolant_temp', 'speed', 'longitude', 'latitude', 'mileage', 'send_time', 'fuel_level_input', 'vehicle_speed', 'obd_power_voltage', 'engine_load', 'throttle_position', 'fuel_consumption']



####################-----------------Trip Module-----------------#######################
class BufferRecordSerializer(DocumentSerializer):
	class Meta:
		model = BufferRecord
		fields = '__all__'


class UserTripSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	trip_log = ListField(required=False)
	imei = StringField(required=True)
	record_date = serializers.DateTimeField(required=False, format="%d-%m-%Y")
	driver_id = StringField(required=False)
	customer_id = StringField(required=False)

	class Meta:
		model = UserTrip
		fields = '__all__'


class UserObdTripSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	trip_log = ListField(required=False)
	imei = StringField(required=True)
	record_date = serializers.DateTimeField(required=False, format="%d-%m-%Y")
	driver_id = StringField(required=False)
	customer_id = StringField(required=False)

	class Meta:
		model = UserObdTrip
		fields = '__all__'


# class FeaturedUserTripSerializer(DocumentSerializer):
# 	measure_id = IntField(required=False)
# 	trip_log = ListField(required=False)
# 	imei = StringField(required=True)
# 	record_date = serializers.DateTimeField(required=False, format="%d-%m-%Y")
# 	driver_id = StringField(required=False)
# 	customer_id = StringField(required=False)

# 	class Meta:
# 		model = FeaturedUserTrip
# 		fields = '__all__'


class TripsMesurementSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	total_distance = ListField(required=False)
	total_time = ListField(required=False)

	class Meta:
		model = TripsMesurement
		fields = '__all__'


class TripsObdMesurementSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	total_distance = ListField(required=False)
	total_time = ListField(required=False)

	class Meta:
		model = TripsObdMesurement
		fields = '__all__'


class TripDateAvailableSerializer(DocumentSerializer):
	record_date_timezone = serializers.DateTimeField(format="%d-%m-%Y")
	class Meta:
		model = UserTrip
		fields = ['record_date_timezone']


class TripObdDateAvailableSerializer(DocumentSerializer):
	record_date_timezone = serializers.DateTimeField(format="%d-%m-%Y")
	class Meta:
		model = UserObdTrip
		fields = ['record_date_timezone']


#-----------------------User trip for backup
class UserTripForBackupSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	trip_log = ListField(required=False)
	imei = StringField(required=True)
	record_date = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
	driver_id = StringField(required=False)
	customer_id = StringField(required=False)
	record_date_timezone = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")

	class Meta:
		model = UserTrip
		fields = '__all__'


class UserObdTripForBackupSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	trip_log = ListField(required=False)
	imei = StringField(required=True)
	record_date = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
	driver_id = StringField(required=False)
	customer_id = StringField(required=False)
	record_date_timezone = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")

	class Meta:
		model = UserObdTrip
		fields = '__all__'



class UserTripBackupSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	trip_log = ListField(required=False)
	imei = StringField(required=True)
	record_date = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
	driver_id = StringField(required=False)
	customer_id = StringField(required=False)
	record_date_timezone = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")

	class Meta:
		model = UserTripBackup
		fields = '__all__'


class TripsMesurementBackupSerializer(DocumentSerializer):
	measure_id = IntField(required=False)
	total_distance = ListField(required=False)
	total_time = ListField(required=False)

	class Meta:
		model = TripsMesurementBackup
		fields = '__all__'

#-------------------------map settings
class MapSettingsSerializer(serializers.ModelSerializer):
	class Meta:
		model = MapSettings
		fields = '__all__'

#------------------------_Settings
class SettingsSerializer(serializers.ModelSerializer):
	imei = serializers.CharField(allow_null=True, allow_blank=True, required=True)
	customer_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	device_name = serializers.CharField(required=False, allow_blank=False, allow_null=True)
	vehicle_type = serializers.CharField(allow_blank=False, allow_null=True, required=False)
	vehicle_color = serializers.CharField(allow_blank=False, allow_null=True, required=False)
	device_reporting_frequency = serializers.CharField(allow_blank=False, allow_null=True, required=False)
	device_reporting_frequency_desc = serializers.CharField(allow_blank=False, allow_null=True, required=False)
	trip_end_timer = serializers.IntegerField(allow_null=True, required=False)
	battery_low_limit = serializers.IntegerField(allow_null=True, required=False)
	device_frequency_value = serializers.IntegerField(allow_null=True, required=False)
	speed_limit = serializers.FloatField(required=False, allow_null=True)
	show_speed = serializers.BooleanField(required=False, allow_null=True)
	show_engine_rpm = serializers.BooleanField(required=False, allow_null=True)
	show_mileage = serializers.BooleanField(required=False, allow_null=True)
	show_fuel_consumption = serializers.BooleanField(required=False, allow_null=True)
	show_engine_temp = serializers.BooleanField(required=False, allow_null=True)
	show_voltage = serializers.BooleanField(required=False, allow_null=True)
	show_engine_load = serializers.BooleanField(required=False, allow_null=True)
	show_throttle_position = serializers.BooleanField(required=False, allow_null=True)
	show_location = serializers.BooleanField(required=False, allow_null=True)
	show_fuel_level = serializers.BooleanField(required=False, allow_null=True)

	email = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	phone = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	secondary_phone = serializers.CharField(allow_blank=True, allow_null=True, required=False) 

	trip_notification = serializers.BooleanField(required=False, allow_null=True)
	trip_email = serializers.BooleanField(required=False, allow_null=True)
	trip_sms = serializers.BooleanField(required=False, allow_null=True)
	engine_notification = serializers.BooleanField(required=False, allow_null=True)
	engine_email = serializers.BooleanField(required=False, allow_null=True)
	engine_sms = serializers.BooleanField(required=False, allow_null=True)
	speed_notification = serializers.BooleanField(required=False, allow_null=True)
	speed_sms = serializers.BooleanField(required=False, allow_null=True)
	speed_email = serializers.BooleanField(required=False, allow_null=True)
	zone_alert_notification = serializers.BooleanField(required=False, allow_null=True)
	harshbraking_notification = serializers.BooleanField(required=False, allow_null=True)
	harshbraking_sms = serializers.BooleanField(required=False, allow_null=True)
	harshbraking_email = serializers.BooleanField(required=False, allow_null=True)
	harshturning_notification = serializers.BooleanField(required=False, allow_null=True)
	harshturning_sms = serializers.BooleanField(required=False, allow_null=True)
	harshturning_email = serializers.BooleanField(required=False, allow_null=True)
	harshacceleration_notification = serializers.BooleanField(required=False, allow_null=True)
	harshacceleration_email = serializers.BooleanField(required=False, allow_null=True)
	harshacceleration_sms = serializers.BooleanField(required=False, allow_null=True)
	sos_notification = serializers.BooleanField(required=False, allow_null=True)
	sos_sms = serializers.BooleanField(required=False, allow_null=True)
	sos_email = serializers.BooleanField(required=False, allow_null=True)
	charging_notification = serializers.BooleanField(required=False, allow_null=True)
	charging_sms = serializers.BooleanField(required=False, allow_null=True)
	charging_email = serializers.BooleanField(required=False, allow_null=True)
	power_notification = serializers.BooleanField(required=False, allow_null=True)
	power_sms = serializers.BooleanField(required=False, allow_null=True)
	power_email = serializers.BooleanField(required=False, allow_null=True)
	show_battery = serializers.BooleanField(required=False, allow_null=True)
	battery_notification = serializers.BooleanField(required=False, allow_null=True)
	battery_email = serializers.BooleanField(required=False, allow_null=True)
	battery_sms = serializers.BooleanField(required=False, allow_null=True)
	attach_dettach_notification = serializers.BooleanField(required=False, allow_null=True)
	attach_dettach_email = serializers.BooleanField(required=False, allow_null=True)
	attach_dettach_sms = serializers.BooleanField(required=False, allow_null=True)
	trip_sensor = serializers.BooleanField(required=False, allow_null=True)
	trip_coordinate = serializers.BooleanField(required=False, allow_null=True)
	global_sms = serializers.BooleanField(required=False, allow_null=True)
	global_email = serializers.BooleanField(required=False, allow_null=True)
	global_notification = serializers.BooleanField(required=False, allow_null=True)
	tow_notification = serializers.BooleanField(required=False, allow_null=True)
	tow_email = serializers.BooleanField(required=False, allow_null=True)
	tow_sms = serializers.BooleanField(required=False, allow_null=True)
	speed_notification_global = serializers.BooleanField(required=False, allow_null=True)
	trip_notification_global = serializers.BooleanField(required=False, allow_null=True)
	engine_notification_global = serializers.BooleanField(required=False, allow_null=True)
	harsh_notification_global = serializers.BooleanField(required=False, allow_null=True)
	sos_notification_global = serializers.BooleanField(required=False, allow_null=True)
	charging_notification_global = serializers.BooleanField(required=False, allow_null=True)
	power_notification_global = serializers.BooleanField(required=False, allow_null=True)
	battery_notification_global = serializers.BooleanField(required=False, allow_null=True)
	attach_dettach_notification_global = serializers.BooleanField(required=False, allow_null=True)
	tow_notification_global = serializers.BooleanField(required=False, allow_null=True)
	mobile_carrier = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	secondary_mobile_carrier = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	fuel_capacity = serializers.FloatField(required=False, allow_null=True)

	warning_notification_global = serializers.BooleanField(required=False, allow_null=True)
	warning_notification = serializers.BooleanField(required=False, allow_null=True)
	warning_email = serializers.BooleanField(required=False, allow_null=True)
	warning_sms = serializers.BooleanField(required=False, allow_null=True)
	

	class Meta:
		model = SettingsModel
		fields = '__all__'


#-----------------------------Reports
class ReportsSerializer(DocumentSerializer):
	imei = StringField(required=True)
	device_name = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	alert_name = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	event_type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	battery_percentage = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	location = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	longitude = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	latitude = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	speed = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	notification_sent = BooleanField(required=False)
	customer_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	speed_status = BooleanField(required=False)

	class Meta:
		model = Reports
		fields = '__all__'


class ZoneNotificationCheckerSerializer(DocumentSerializer):
	imei = StringField(required=True)
	event_type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	customer_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	zone = serializers.IntegerField(allow_null=True, required=False)
	zone_alert = serializers.IntegerField(allow_null=True, required=False)

	class Meta:
		model = ZoneNotificationChecker
		fields = '__all__'

#-------------------------------Events
class NotificationsBackupSerializer(DocumentSerializer):
	class Meta:
		model = NotificationsBackup
		fields = '__all__'
		
class NotificationsSerializer(DocumentSerializer):
	imei = StringField(required=True)
	customer_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	title = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	body = serializers.CharField(allow_null=True, allow_blank=True, required=False)
	type = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	longitude = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	latitude = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	alert_name  = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	event  = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	battery_percentage  = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	location  = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	speed  = serializers.CharField(allow_blank=True, allow_null=True, required=False)
	record_date_timezone = DateTimeField()

	class Meta:
		model = Notifications
		fields = '__all__'


class NotificationsReadSerializer(DocumentSerializer):
	imei = serializers.CharField(required=False)
	customer_id = serializers.CharField(required=False)
	title = serializers.CharField(required=False)
	body = serializers.CharField(required=False)
	record_date_timezone = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
	record_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

	class Meta:
		model = Notifications
		fields = '__all__'


class OdometereSerializer(serializers.ModelSerializer):
	class Meta:
		model = Odometere
		fields = '__all__'


class TripEventsSerializer(serializers.ModelSerializer):
	imei = serializers.CharField(required=False)
	type = serializers.CharField(required=False)
	location = serializers.CharField(required=False)
	date = serializers.DateField(required=False)
	time = serializers.TimeField(required=False)
	record_date = serializers.DateField(required=False)
	customer_id = serializers.IntegerField(required=False, allow_null=True)

	class Meta:
		model = TripEvents
		fields = '__all__'


class VoltageSerializer(serializers.ModelSerializer):
	class Meta:
		model = VoltageModel
		fields = '__all__'


class HarshEventSerializer(serializers.ModelSerializer):
	class Meta:
		model = HarshBehaviourEvent
		fields = '__all__'


class FuelEconomySerializer(serializers.ModelSerializer):
	class Meta:
		model = FuelEconomy
		fields = '__all__'


class EmissionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Emission
		fields = '__all__'

class FuelConsumptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = FuelConsumption
		fields = '__all__'


class DriverScoreSerializer(serializers.ModelSerializer):
	class Meta:
		model = DriverScore
		fields = '__all__'


class DtcEventsSerializer(serializers.ModelSerializer):
	class Meta:
		model = DtcEvents
		fields = '__all__'


class DtcEventsReadSerializer(serializers.ModelSerializer):
	record_time = serializers.TimeField(format="%H:%M:%S")
	class Meta:
		model = DtcEvents
		fields = '__all__'


class ObdDtcEventSerializer(serializers.ModelSerializer):
	class Meta:
		model = OBDDtcEvents
		fields = '__all__'


class ObdDtcEventsReadSerializer(serializers.ModelSerializer):
	record_time = serializers.TimeField(format="%H:%M:%S")
	class Meta:
		model = OBDDtcEvents
		fields = '__all__'

#---------------------Location
class LocationSerializer(DocumentSerializer):
	longitude = StringField(required=True)
	latitude = StringField(required=True)
	location_name = StringField(required=True)

	class Meta:
		model = Location
		fields = ['longitude', 'latitude', 'location_name']


#---------------------Country and States


#---------------------individual track
class IndividualTrackingSerializer(serializers.ModelSerializer):
	class Meta:
		model = IndividualTracking
		fields = '__all__'


#--------------------SMS logs
class SmsLogSerializer(DocumentSerializer):
	customer_id = StringField(required=True)
	imei = StringField(required=True)
	message = StringField(required=True)

	class Meta:
		model = SmsLog
		fields = '__all__'


#----------------GPS Events
class GpsEventsDateSerializer(DocumentSerializer):
	record_date_timezone = serializers.DateTimeField(format="%d-%m-%Y")
	class Meta:
		model = Notifications
		fields = ['record_date_timezone']


#---------------Trip Cron 
class TripCalculationGLCronSerializer(DocumentSerializer):
	class Meta:
		model = TripCalculationGLCron
		fields = '__all__'


class TripCalculationObdCronSerializer(DocumentSerializer):
	class Meta:
		model = TripCalculationObdCron
		fields = '__all__'


#------------Free Trial
class FreeTrialSerializer(serializers.ModelSerializer):
	class Meta:
		model = FreeTrialModel
		fields = '__all__'


#----------Ideal time serializer
class GpsIdealTimeSerializer(serializers.ModelSerializer):
	class Meta:
		model = GpsIdealTime
		fields = '__all__'


#----------Battery Train
class BatteryDrainSerializer(serializers.ModelSerializer):
	class Meta:
		model = BatteryDrain
		fields = '__all__'


#-------Fuel level tracker
class FuelLevelTrackerSerializer(serializers.ModelSerializer):
	class Meta:
		model = FuelLevelTracker
		fields = '__all__'