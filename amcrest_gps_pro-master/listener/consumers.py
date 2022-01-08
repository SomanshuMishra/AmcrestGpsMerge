import asyncio
import json
from datetime import datetime, timedelta
import time
import _thread

from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.db import connections, close_old_connections


from .models import *
from .serializers import *

from .save_for_trip import *

from app.models import UserTrip, TripsMesurement, SettingsModel, GlBufferRecord
from app.serializers import UserTripSerializer, TripsMesurementSerializer, TripCalculationDataSerializer, BufferRecordSerializer

from app.engine_notification.notification_maker import *
from app.zone_notification import zone_checker, zone_checker_obd
from app.harsh_notification import harsh_notification_maker
from app.speed_notifications import speed_notification_maker, obd_speed_notification_maker
from app.trip_notification import trip_notification_maker, gl_trip_notification_maker 
from app.attach_dettach_notification import ad_notification_maker
from app.events import harsh_events
from app.sos_notifications import sos_notification_maker
from app.power_notification import power_notification_maker
from app.charging_notification import charging_notification_maker
from app.battery_notification import battery_notification_maker, battery_lowest_check
from app.alert_notification import tow_notification_maker
from app.dtc_alert import dtc_alert_notification_maker
from app.warning_alert import warning_alert_notification

time_fmt = '%Y-%m-%d %H:%M:%S'

from asgiref.sync import async_to_sync

count = 1

lat_lang = ['0', '00', 'nan', 'None']

protocol_to_be_calculate = ['+RESP:GTIGN', '+RESP:GTIGF', '+RESP:GTOBD']
protocol_to_be_calculate_gl = ['+RESP:GTFRI', '+RESP:GTSTT', '+BUFF:GTFRI', '+BUFF:GTSTT']

protocol_for_speed_notification = ['+RESP:GTOBD', '+RESP:GTHBM']
protocol_for_speed_notification_gl = ['+RESP:GTFRI']
buffer_protocol = ["+BUFF:GTIGN", "+BUFF:GTIGF", "+BUFF:GTHBM", "+BUFF:GTFRI", "+BUFF:GTOBD", "+BUFF:GTJES", "+BUFF:GTBPL", "+BUFF:GTCRA", "+BUFF:GTOSM", "+BUFF:GTOPN", "+BUFF:GTOPF"]
gl_buffer_record = ["+BUFF:GTSTT", "+BUFF:GTFRI"]

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



class ObdConsumer(AsyncConsumer):
	async def websocket_connect(self, event):
		imei = self.scope['url_route']['kwargs']['imei']
		self.imei = imei
		await self.channel_layer.group_add(
				imei,
				self.channel_name
		
			)
		# await self.accept()
		await self.send({
            "type": "websocket.accept"
        })



	async def websocket_receive(self, event):
		close_old_connections()
		imei = self.scope['url_route']['kwargs']['imei']
		details = event.get('text', None)
		details = json.loads(details)
		self.chat_room = imei
		if details:
			details = details[0]

			if details.get('from', None):

				_thread.start_new_thread(save_records_listener, (details.get('details'),))

				await self.create_gl_trip_cron(imei, details, details.get('protocol', None))
				await self.zone_checker_gl(imei, details, details.get('protocol', None))

				await self.speed_limit_notification_gl(imei, details, details.get('protocol', None))
				await self.sos_notification(imei, details, details.get('protocol', None))
				await self.power_notification(imei, details, details.get('protocol', None))
				await self.charging_notification(imei, details, details.get('protocol', None))
				await self.battery_notification(imei, details, details.get('protocol', None))

				await self.trip_notification_gl(imei, details, details.get('protocol', None))
				close_old_connections()
			else:
				# await self.create_obd_record(details)
				
				_thread.start_new_thread(save_records_obd_listener, (details.get('details'),))
				_thread.start_new_thread(speed_alert_obd, (details.get('details'),))
				

				await self.zone_checker(imei, details, details.get('protocol', None))
				await self.create_obd_trip_cron(imei, details, details.get('protocol', None))

				await self.send_alert_record(imei, details, details.get('protocol', None))
				
				await self.harsh_behaviour_notification(imei, details, details.get('protocol', None))
				await self.create_buffer_record(imei, details, details.get('protocol', None))
				await self.attach_dettach_record(imei, details, details.get('protocol', None))

				#-------commented

				# _thread.start_new_thread(fuel_economy_cal, (details.get('details'),)) //Topfly fuel economy
				# _thread.start_new_thread(notify_device, (imei, details, details.get('protocol', None),))
				# _thread.start_new_thread(obd_zone_notification, (details.get('details'),))
				# await self.notify_device(imei, details, details.get('protocol', None))
				# await self.speed_limit_notification(imei, details, details.get('protocol', None))

				close_old_connections()
		else:
			pass


	async def obd_message(self, event):
		await self.send({
			"type":"websocket.send",
			"text":event['text']
			})

	async def websocket_disconnect(self, event):
		print("Disconnected", event)


	@database_sync_to_async
	def attach_dettach_record(self, imei, details, protocol):
		close_old_connections()
		if protocol == '+RESP:GTOPN':
			_thread.start_new_thread(ad_notification_maker.attach_notification_receiver, (imei, details.get('details')))
		elif protocol == '+RESP:GTOPF':
			_thread.start_new_thread(ad_notification_maker.dettach_notification_receiver, (imei, details.get('details')))

	
	def check_last_location(self, longitude, latitude, imei):
		gtigf = IgnitionOnoff.objects.filter(imei = imei).last()
		close_old_connections()
		if gtigf:
			if gtigf.longitude == longitude and gtigf.latitude == latitude:
				return False
		return True

	def check_last_location_gl(self, longitude, latitude, imei):
		stt = SttMarkers.objects.filter(imei = imei).last()
		close_old_connections()
		if stt:
			if stt.longitude == float(longitude) or stt.latitude == float(latitude):
				return False
		return True


	def check_last_location_gl_fri(self, longitude, latitude, imei):
		stt = GLFriMarkers.objects.filter(imei = imei).last()
		close_old_connections()
		if stt:
			if stt.longitude == flaot(longitude) or stt.latitude == float(latitude):
				return False
			return True
		return True

	def check_trip_started(self, imei):
		protocol_record = TripProtocolRecord.objects.filter(imei=imei).last()
		close_old_connections()
		if protocol_record:
			if protocol_record.protocol == 'GTSTT':
				return True
			return False
		return False

	def get_trip_started_log(self, imei):
		stt = SttMarkers.objects.filter(imei = imei, state=42).last()
		if stt:
			serializer = SttMarkersSerializer(stt)
			return serializer.data
		return {} 

	def check_last_mileage_gl(self, mileage, imei):
		glfri = GLFriMarkers.objects.filter(imei = imei).last()
		stt = SttMarkers.objects.filter(imei = imei).last()
		if glfri and stt:
			if stt.mileage == float(mileage):
				return False
		return True

	def delete_trip_protocol_recorder(self, imei):
		protocol_record = TripProtocolRecord.objects.filter(imei=imei).all()
		if protocol_record:
			protocol_record.delete()
		close_old_connections()

	@database_sync_to_async
	def trip_notification_obd(self, imei, details, protocol):
		close_old_connections()
		if protocol in protocol_to_be_calculate:
			try:
				lat = details['details'].get('latitude')
			except(Exception)as e:
				lat = None

			try:
				lang = details['details'].get('longitude')
			except(Exception)as e:
				lang = None

			if lat != None and lang != None and lat not in lat_lang and lang not in lat_lang:
				if protocol == '+RESP:GTOBD':
					pass
				elif protocol == '+RESP:GTIGF' or protocol == '+RESP:GTIGN':
					if protocol == '+RESP:GTIGF':
						_thread.start_new_thread(trip_notification_maker.trip_end_notification_receiver, (imei, details.get('details')))
					elif protocol == '+RESP:GTIGN':
						_thread.start_new_thread(trip_notification_maker.trip_start_notification_receiver, (imei, details.get('details')))
					else:
						pass


	@database_sync_to_async
	def send_alert_record(self, imei, details, protocol):
		if protocol == "+RESP:GTTOW":
			_thread.start_new_thread(tow_notification_maker.alert_notification_receiver, (imei, details.get('details')))
		elif protocol == "+RESP:GTDTC":
			_thread.start_new_thread(dtc_alert_notification_maker.dtc_alert_notification_receiver, (imei, details.get('details')))
		elif protocol == "+RESP:GTOBDTC":
			# print(details.get('details'))
			_thread.start_new_thread(warning_alert_notification.warning_alert_notification_receiver, (imei, details.get('details')))

	@database_sync_to_async
	def create_obd_trip_cron(self, imei, details, protocol):
		close_old_connections()
		if protocol in protocol_to_be_calculate:
			try:
				lat = details['details'].get('latitude')
			except(Exception)as e:
				lat = None


			try:
				lang = details['details'].get('longitude')
			except(Exception)as e:
				lang = None

			try:
				mileage = float(details['details'].get('mileage'))
			except(Exception)as e:
				mileage = 0

			try:
				speed = float(details['details'].get('speed'))
			except(Exception)as e:
				speed = 0

			try:
				gps_accuracy = int(details['details'].get('gps_accuracy', None))
			except(Exception)as e:
				gps_accuracy = 0

			if speed>0:
				try:
					import asyncio
					_thread.start_new_thread(save_for_obd_trip_cron, (imei,details, protocol))
				except(Exception)as e:
					print(e)
					pass
			elif protocol == '+RESP:GTIGN' or protocol == '+RESP:GTIGF':
				try:
					import asyncio
					_thread.start_new_thread(save_for_obd_trip_cron, (imei,details, protocol))
				except(Exception)as e:
					print(e)
					pass

	@database_sync_to_async
	def create_gl_trip_cron(self, imei, details, protocol):
		close_old_connections()
		if protocol in protocol_to_be_calculate_gl:
			try:
				lat = details['details'].get('latitude')
			except(Exception)as e:
				lat = None


			try:
				lang = details['details'].get('longitude')
			except(Exception)as e:
				lang = None

			try:
				mileage = float(details['details'].get('mileage'))
			except(Exception)as e:
				mileage = 0

			try:
				speed = float(details['details'].get('speed'))
			except(Exception)as e:
				speed = 0

			try:
				gps_accuracy = int(details['details'].get('gps_accuracy', None))
			except(Exception)as e:
				gps_accuracy = 0


			if gps_accuracy>0 and speed>0:
				try:
					import asyncio
					loop = asyncio.new_event_loop()
					loop.run_in_executor(None, save_for_trip_cron, [imei,details, protocol])
				except(Exception)as e:
					print(e)
					pass
			elif protocol == '+RESP:GTSTT' or protocol == '+BUFF:GTSTT':
				try:
					import asyncio
					loop = asyncio.new_event_loop()
					loop.run_in_executor(None, save_for_trip_cron, [imei,details, protocol])
				except(Exception)as e:
					print(e)
					pass


	@database_sync_to_async
	def trip_notification_gl(self, imei, details, protocol):
		close_old_connections()
		if protocol in protocol_to_be_calculate_gl:
			try:
				lat = details['details'].get('latitude')
			except(Exception)as e:
				lat = None


			try:
				lang = details['details'].get('longitude')
			except(Exception)as e:
				lang = None

			try:
				mileage = details['details'].get('mileage')
			except(Exception)as e:
				mileage = None

			try:
				speed = details['details'].get('speed')
			except(Exception)as e:
				speed = None

			try:
				gps_accuracy = int(details['details'].get('gps_accuracy', None))
			except(Exception)as e:
				gps_accuracy = 0

					
			
			checking_sensor = self.check_sensor(imei)
			if lat != None and lang != None and lat not in lat_lang and lang not in lat_lang:
				if protocol == '+RESP:GTFRI':
					
					checking_trip = self.check_trip_running(imei)
					check_location = self.check_last_location_gl(lang, lat, imei)
					check_mileage = self.check_last_mileage_gl(mileage, imei)

					if checking_trip and check_location and gps_accuracy>0 and check_mileage:
						if not checking_sensor and self.check_trip_started(imei):
							trip_started_log = self.get_trip_started_log(imei)
							_thread.start_new_thread(gl_trip_notification_maker.gl_trip_start_notification_receiver, (imei, trip_started_log))
							self.delete_trip_protocol_recorder(imei)
					elif check_location and gps_accuracy>0 and check_mileage:
						if not checking_sensor and self.check_trip_started(imei):
							trip_started_log = self.get_trip_started_log(imei)
							_thread.start_new_thread(gl_trip_notification_maker.gl_trip_start_notification_receiver, (imei, trip_started_log))
							self.delete_trip_protocol_recorder(imei)

				if protocol == '+RESP:GTSTT':
					if details.get('details', None):
						if details['details'].get('state') == '41' or details['details'].get('state') == '21':
							_thread.start_new_thread(gl_trip_notification_maker.gl_trip_end_notification_receiver, (imei, details.get('details')))
							self.delete_trip_protocol_recorder(imei)
							

						elif details['details'].get('state') == '42' or details['details'].get('state') == '22':
							pro_serializer = TripProtocolRecordSerializer(data={
									'imei':imei,
									'protocol':'GTSTT'
								})

							if pro_serializer.is_valid():
								pro_serializer.save()
								close_old_connections()
								
							if checking_sensor:
								_thread.start_new_thread(gl_trip_notification_maker.gl_trip_start_notification_receiver, (imei, details.get('details')))
								self.delete_trip_protocol_recorder(imei)
			pass

	def check_sensor(self, imei):
		setting_int = SettingsModel.objects.filter(imei=imei).last()
		close_old_connections()
		if setting_int:
			if setting_int.trip_sensor == True:
				return True
			return False
		return False

	def check_trip_running(self, imei):
		uphold_time = TripCalculationGLCron.objects.filter(imei=imei).first()
		close_old_connections()
		if uphold_time:
			return True
		return False

	@database_sync_to_async
	def harsh_behaviour_notification(self, imei, details, protocol):
		close_old_connections()
		if protocol == '+RESP:GTHBM':
			_thread.start_new_thread(harsh_notification_maker.harsh_notification_receiver, (imei, details.get('details')))
			_thread.start_new_thread(harsh_events.harsh_event_receiver, (imei, details.get('details')))

		if protocol == '+RESP:GTHBA':
			_thread.start_new_thread(harsh_notification_maker.harsh_notification_receiver, (imei, details.get('details')))

	@database_sync_to_async
	def power_notification(self, imei, details, protocol):
		close_old_connections()
		if protocol == '+RESP:GTPNA':
			_thread.start_new_thread(power_notification_maker.power_on_notification_receiver, (imei, details.get('details')))
		elif protocol == '+RESP:GTPFA':
			_thread.start_new_thread(power_notification_maker.power_off_notification_receiver, (imei, details.get('details')))


	@database_sync_to_async
	def charging_notification(self, imei, details, protocol):
		close_old_connections()
		if protocol == '+RESP:GTBTC':
			_thread.start_new_thread(charging_notification_maker.charging_on_notification_receiver, (imei, details.get('details')))
		elif protocol == '+RESP:GTSTC':
			_thread.start_new_thread(charging_notification_maker.charging_off_notification_receiver, (imei, details.get('details')))

	@database_sync_to_async
	def battery_notification(self, imei, details, protocol):
		close_old_connections()
		try:
			gps_accuracy = int(details['details'].get('gps_accuracy', None))
		except(Exception)as e:
			gps_accuracy = 0

		if protocol == '+RESP:GTFRI' and gps_accuracy>0:
			
			_thread.start_new_thread(battery_notification_maker.battery_notification_receiver, (imei, details.get('details')))
			_thread.start_new_thread(battery_lowest_check.battery_notification_receiver, (imei, details.get('details')))
			

	@database_sync_to_async
	def speed_limit_notification(self, imei, details, protocol):
		close_old_connections()
		if protocol == '+RESP:GTSPD':
			try:
				speed = float(details['details'].get('speed', None))
			except(Exception)as e:
				speed = 0

			if speed>0:
				_thread.start_new_thread(obd_speed_notification_maker.speed_notification_receiver, (imei, details.get('details')))


	@database_sync_to_async
	def speed_limit_notification_gl(self, imei, details, protocol):
		close_old_connections()
		if protocol in protocol_for_speed_notification_gl:
			try:
				gps_accuracy = int(details['details'].get('gps_accuracy', None))
			except(Exception)as e:
				gps_accuracy = 0

			try:
				speed = float(details['details'].get('speed', None))
			except(Exception)as e:
				speed = 0

			if speed>0 and gps_accuracy>0:
				_thread.start_new_thread(speed_notification_maker.speed_notification_receiver, (imei, details.get('details')))
		close_old_connections()

	@database_sync_to_async
	def notify_device(self, imei, details, protocol):
		# print(details)
		close_old_connections()
		if protocol == '+RESP:GTIGN':
			_thread.start_new_thread(engine_started_notification_receiver, (imei, details.get('details')))

		elif protocol == '+RESP:GTIGF':
			_thread.start_new_thread(engine_turnoff_notification_receiver, (imei, details.get('details')))

			# save_for_trip_end
		close_old_connections()

	@database_sync_to_async
	def zone_checker(self, imei, details, protocol):
		close_old_connections()
		if protocol in ['+RESP:GTOBD']:
			_thread.start_new_thread(zone_checker_obd.zone_checker, (imei, details.get('details')))
		close_old_connections()
			


	@database_sync_to_async
	def zone_checker_gl(self, imei, details, protocol):
		if protocol in ['+RESP:GTFRI']:
			_thread.start_new_thread(zone_checker.zone_checker, (imei, details.get('details')))
		close_old_connections()

	@database_sync_to_async
	def sos_notification(self, imei, details, protocol):
		if protocol in ['+RESP:GTSOS']:
			_thread.start_new_thread(sos_notification_maker.sos_notification_receiver, (imei, details.get('details')))
		close_old_connections()

	@database_sync_to_async
	def create_obd_record(self, details):
		serializer = protocol_serializer[details.get('protocol', None)](data=details['details'])
		if serializer.is_valid():
			serializer.save()
		else:
			pass


	@database_sync_to_async
	def create_gl_obd_record(self, details):

		serializer = gl_protocol_serializer[details.get('protocol', None)](data=details['details'])
		try:
			if serializer.is_valid():
				try:
					serializer.save()
				except(Exception)as e:
					print(e)
				close_old_connections()
				pass
			else:
				pass
		except(Exception)as e:
			pass

	@database_sync_to_async
	def create_buffer_record(self, imei, details, protocol):
		if protocol in buffer_protocol:
			data = {}
			data['imei'] = imei
			data['details'] = details.get('details')
			serializer = BufferRecordSerializer(data=data)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()
			else:
				pass


	@database_sync_to_async
	def create_gl_buffer_record(self, imei, details, protocol):
		if protocol in gl_buffer_record:
			if imei and details:
				gl_record = GlBufferRecord(
					imei=imei,
					details = details.get('details')
					)
				gl_record.save()
		close_old_connections()



