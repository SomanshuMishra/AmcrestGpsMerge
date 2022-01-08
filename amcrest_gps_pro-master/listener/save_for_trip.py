from django.db import close_old_connections

import json
import _thread

from .models import *
from .serializers import *

from app.models import UserTrip, TripsMesurement, SettingsModel, TripCalculationGLCron, TripCalculationObdCron, TripEndRecord
from app.serializers import UserTripSerializer, TripsMesurementSerializer, TripCalculationDataSerializer, BufferRecordSerializer

from app.speed_notifications import speed_notification_maker, obd_speed_notification_maker

from app.events import fuel_economy
from app.zone_notification import obd_zone_notification_maker
from app.engine_notification.notification_maker import *

protocol_serializer = {
	"+RESP:GTIGN" : IgnitionOnoffSerializer,
	"+RESP:GTIGF" : IgnitionOnoffSerializer,
	"+RESP:GTHBM" : HarshBehaviourSerializer,
	"+RESP:GTFRI" : FriMarkersSerializer,
	"+RESP:GTOBD" : ObdMarkersSerializer,
	"+RESP:GTJES" : EngineSummarySerializer,
	"+RESP:GTBPL" : BatteryLowSerializer,
	"+RESP:GTCRA" : CrashReportSerializer,
	"+RESP:GTOSM" : ObdStatusReportSerializer,
	"+RESP:GTOPN" : AttachDettachSerializer,
	"+RESP:GTOPF" : AttachDettachSerializer,
	"+RESP:GTTOW" : AlertRecordsSerializer,
	"+RESP:GTDTC" : DTCRecordsSerializer,
	"+RESP:GTIDN" : IdleDeviceSerializer,
	"+RESP:GTIDF" : IdleDeviceSerializer,
	"+RESP:GTHBA" : HarshAccelerationSerializer,
	"+RESP:GTSPD" : SpeedAlerObdSerializer,
	"+RESP:GTGEO" : GeoFenceObdSerializer,
	"+RESP:GTOBDTC" : OBDTCRecordsSerializer,

	"+BUFF:GTIGN" : IgnitionOnoffSerializer,
	"+BUFF:GTIGF" : IgnitionOnoffSerializer,
	"+BUFF:GTHBM" : HarshBehaviourSerializer,
	"+BUFF:GTFRI" : FriMarkersSerializer,
	"+BUFF:GTOBD" : ObdMarkersSerializer,
	"+BUFF:GTJES" : EngineSummarySerializer,
	"+BUFF:GTBPL" : BatteryLowSerializer,
	"+BUFF:GTCRA" : CrashReportSerializer,
	"+BUFF:GTOSM" : ObdStatusReportSerializer,
	"+BUFF:GTOPN" : AttachDettachSerializer,
	"+BUFF:GTOPF" : AttachDettachSerializer,

	"+ACK:GTGEO"  : GeoFenceAckSerializer,

}

gl_protocol_serializer = {
	"+RESP:GTFRI" : GLFriMarkersSerializer,
	"+RESP:GTSTT" : SttMarkersSerializer,
	"+RESP:GTBTC" : BatteryModelSerializer,
	"+RESP:GTSTC" : BatteryModelSerializer,
	"+RESP:GTPNA" : PowerSerializer,
	"+RESP:GTPFA" : PowerSerializer,
	"+RESP:GTSOS" : SOSSerializer,

	"+BUFF:GTFRI" : GLFriMarkersSerializer,
	"+BUFF:GTSTT" : SttMarkersSerializer,
	"+BUFF:GTBTC" : BatteryModelSerializer,
	"+BUFF:GTSTC" : BatteryModelSerializer,
	"+BUFF:GTPNA" : PowerSerializer,
	"+BUFF:GTPFA" : PowerSerializer,
	"+BUFF:GTSOS" : SOSSerializer,

}

def notify_device(imei, details, protocol):
	# print(details)
	close_old_connections()
	if protocol == '+RESP:GTIGN':
		_thread.start_new_thread(engine_started_notification_receiver, (imei, details.get('details')))

	elif protocol == '+RESP:GTIGF':
		_thread.start_new_thread(engine_turnoff_notification_receiver, (imei, details.get('details')))


def fuel_economy_cal(details):
	if details.get('protocol', None) == '+RESP:GTJES':
		_thread.start_new_thread(fuel_economy.fuel_economy_module_new, (details.get('imei'), details))

def obd_zone_notification(details):
	if details.get('protocol', None) == '+RESP:GTGEO':
		_thread.start_new_thread(obd_zone_notification_maker.start_zone_notification, (details.get('imei'), details))

def save_records_listener(details):
	print(details)
	if details.get('send_time', None):
		serializer = gl_protocol_serializer[details.get('report_name', None)](data=details)
		try:
			if serializer.is_valid():
				try:
					serializer.save()
				except(Exception)as e:
					print(e)
				close_old_connections()
				pass
			else:
				print(serializer.errors)
				pass
		except(Exception)as e:
			print(e)
			pass
	pass


def save_records_obd_listener(details):
	print(details)
	serializer = protocol_serializer[details.get('protocol', None)](data=details)
	try:
		if serializer.is_valid():
			try:
				serializer.save()
			except(Exception)as e:
				print(e)
			close_old_connections()
			pass
		else:
			print(serializer.errors, '----------')
			pass

		if details.get('protocol', None) == '+RESP:GTIGN':
			_thread.start_new_thread(engine_started_notification_receiver, (details.get('imei'), details))

		elif details.get('protocol', None) == '+RESP:GTIGF':
			_thread.start_new_thread(engine_turnoff_notification_receiver, (details.get('imei'), details))

	except(Exception)as e:
		print(e)
		pass
	pass


def speed_alert_obd(details):
	if details.get('protocol', None) == '+RESP:GTSPD':
		# print(details)
		try:
			speed = float(details.get('speed', None))
		except(Exception)as e:
			speed = 0

		if speed>0:
			_thread.start_new_thread(obd_speed_notification_maker.speed_notification_receiver, (details.get('imei'), details))





def save_for_trip_end(args):
	try:
		imei = args[0]
	except(Exception)as e:
		imei = None

	try:
		details = args[1]
	except(Exception)as e:
		details = None

	try:
		protocol = args[2]
	except(Exception)as e:
		protocol = None

	if imei and details and protocol:
		try:
			trip_end = TripEndRecord(
					imei=imei,
					protocol = protocol,
					details = details
				)
			trip_end.save()
		except(Exception)as e:
			print(e)
			pass

def save_for_trip_cron(args):
	try:
		imei =args[0]
	except(Exception)as e:
		imei = None

	try:
		details = args[1]
	except(Exception)as e:
		details = None

	try:
		protocol = args[2]
	except(Exception)as e:
		protocol = None

	try:
		mileage = float(details['details'].get('mileage'))
	except(Exception)as e:
		mileage = 0


	try:
		send_time = int(details['details'].get('send_time'))
	except(Exception)as e:
		send_time = 0

	if imei and details and protocol:
		# print(details.get('details'))
		try:
			trip_cal = TripCalculationGLCron(
					imei=imei,
					details = details.get('details'),
					protocol = protocol,
					mileage = mileage,
					send_time = send_time
				)
		except(Exception)as e:
			print(e)
			pass


		try:
			trip_cal.save()
			close_old_connections()
		except(Exception)as e:
			print(e)
			pass
		close_old_connections()
		pass


def save_for_obd_trip_cron(imei, details, protocol):
	try:
		imei =imei
	except(Exception)as e:
		imei = None

	try:
		details = details
	except(Exception)as e:
		details = None

	try:
		protocol = protocol
	except(Exception)as e:
		protocol = None

	try:
		mileage = float(details['details'].get('mileage'))
	except(Exception)as e:
		mileage = 0


	try:
		send_time = int(details['details'].get('send_time'))
	except(Exception)as e:
		send_time = 0

	if imei and details and protocol:
		try:
			trip_cal = TripCalculationObdCron(
					imei=imei,
					details = details.get('details'),
					protocol = protocol,
					mileage = mileage,
					send_time = send_time
				)
		except(Exception)as e:
			print(e)
			pass


		try:
			trip_cal.save()
			close_old_connections()
		except(Exception)as e:
			print(e)
			pass
		close_old_connections()
		pass