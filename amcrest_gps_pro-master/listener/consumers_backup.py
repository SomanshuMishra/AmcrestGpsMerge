

import asyncio
import json
from datetime import datetime, timedelta
import time
import _thread

from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from .models import *
from .serializers import *

from app.models import UserTrip, TripsMesurement
from app.serializers import UserTripSerializer, TripsMesurementSerializer, TripCalculationDataSerializer

from app.notification_maker import *
from app.zone_notification import zone_checker
from app.harsh_notification import harsh_notification_maker
from app.speed_notifications import speed_notification_maker
from app.trip_notification import trip_notification_maker
from app.events import harsh_events

time_fmt = '%Y-%m-%d %H:%M:%S'

count = 1

protocol_to_be_calculate = ['+RESP:GTIGN', '+RESP:GTIGF', '+RESP:GTOBD', '+BUFF:GTIGN', '+BUFF:GTIGF', '+BUFF:GTOBD']
protocol_for_speed_notification = ['+RESP:GTIGN', '+RESP:GTIGF', '+RESP:GTOBD', '+RESP:GTHBM', '+BUFF:GTIGN', '+BUFF:GTIGF', '+BUFF:GTOBD', '+BUFF:GTHBM']

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

}



class ObdConsumer(AsyncConsumer):
	async def websocket_connect(self, event):
		imei = self.scope['url_route']['kwargs']['imei']
		await self.channel_layer.group_add(
				imei,
				self.channel_name
		
			)
		await self.send({
            "type": "websocket.accept"
        })



	async def websocket_receive(self, event):
		imei = self.scope['url_route']['kwargs']['imei']
		details = event.get('text', None)
		details = json.loads(details)
		self.chat_room = imei
		if details:
			details = details[0]
			await self.channel_layer.group_send(
					self.chat_room,
					{
						"type":"obd_message",
						"text": json.dumps(details)
					}
				)
			await self.create_obd_record(details)
			await self.create_trip_calulation_record(imei, details, details.get('protocol', None))
			await self.notify_device(imei, details, details.get('protocol', None))
			await self.zone_checker(imei, details, details.get('protocol', None))
			await self.harsh_behaviour_notification(imei, details, details.get('protocol', None))
			await self.speed_limit_notification(imei, details, details.get('protocol', None))
		else:
			print('empty')


	async def obd_message(self, event):
		await self.send({
			"type":"websocket.send",
			"text":event['text']
			})


	async def websocket_disconnect(self, event):
		print("Disconnected", event)

	@database_sync_to_async
	def create_trip_calulation_record(self, imei, details, protocol):
		if protocol in protocol_to_be_calculate:
			print(protocol, 'protocol-----------------')
			serializer = TripCalculationDataSerializer(data={
					'imei':imei,
					'_details': json.dumps(details)
				})

			if serializer.is_valid():
				serializer.save()
				if protocol == '+RESP:GTIGF' or protocol == '+BUFF:GTIGF':
					_thread.start_new_thread(trip_notification_maker.trip_end_notification_receiver, (imei, details.get('details')))
				elif protocol == '+RESP:GTIGN' or protocol == '+BUFF:GTIGN':
					_thread.start_new_thread(trip_notification_maker.trip_start_notification_receiver, (imei, details.get('details')))
			else:
				print(serializer.errors)
				pass

	@database_sync_to_async
	def harsh_behaviour_notification(self, imei, details, protocol):
		if protocol == '+RESP:GTHBM' or protocol == '+BUFF:GTHBM':
			_thread.start_new_thread(harsh_notification_maker.harsh_notification_receiver, (imei, details.get('details')))
			_thread.start_new_thread(harsh_events.harsh_event_receiver, (imei, details.get('details')))

	@database_sync_to_async
	def speed_limit_notification(self, imei, details, protocol):
		if protocol in protocol_for_speed_notification:
			_thread.start_new_thread(speed_notification_maker.speed_notification_receiver, (imei, details.get('details')))
			
	@database_sync_to_async
	def notify_device(self, imei, details, protocol):
		if protocol == '+RESP:GTIGN' or protocol == '+BUFF:GTIGN':
			_thread.start_new_thread(engine_started_notification_receiver, (imei, details.get('details')))

		elif protocol == '+RESP:GTIGF' or protocol == '+BUFF:GTIGF':
			_thread.start_new_thread(engine_turnoff_notification_receiver, (imei, details.get('details')))

	@database_sync_to_async
	def zone_checker(self, imei, details, protocol):
		if protocol in ['+RESP:GTIGN', '+RESP:GTIGF',  '+RESP:GTOBD', '+BUFF:GTIGN', '+BUFF:GTIGF',  '+BUFF:GTOBD']:
			_thread.start_new_thread(zone_checker.zone_checker, (imei, details.get('details')))
			

	@database_sync_to_async
	def create_obd_record(self, details):
		serializer = protocol_serializer[details.get('protocol', None)](data=details['details'])
		if serializer.is_valid():
			serializer.save()
		else:
			print(serializer.errors,'--------------------')


