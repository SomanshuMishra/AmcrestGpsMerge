from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate
from django.conf import settings
from geopy.geocoders import Nominatim

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q as queue
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from app.events import main_location_machine

import string
import random
import datetime
from datetime import timedelta
import time

from .serializers import *
from .models import *


from listener.models import * 
from listener.serializers import *

from services.models import *
from services.serializers import *


exclude_obd = [None, 0, 0.0]
time_fmt = '%Y-%m-%d %H:%M:%S'



class ObdZoneApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request, customer_id):
		if request.data:
			request.data['customer_id'] = customer_id
			serializer = ZoneObdSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return JsonResponse({'message':'Zone OBD Created Successfully', 'status':True, 'status_code':200, 'zone':serializer.data}, status=200)
			return JsonResponse({'message':'Error during creating zone', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Bad request', 'status':False, 'status_code':400}, status=200)


	def get(self, request, customer_id):
		zone = ZoneObd.objects.filter(customer_id=customer_id).all()
		if zone:
			serializer = ZoneObdSerializer(zone, many=True)
			return JsonResponse({'message':'Zone list successfull', 'status':True, 'status_code':200, 'zone':serializer.data}, status=200)
		return JsonResponse({'message':'List of zones', 'status':True, 'status_code':200, 'zone':[]}, status=200)


class ObdZoneIndividualView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, id):
		try:
			zone = ZoneObd.objects.filter(id=id).first()
			close_old_connections()
		except(Exception)as e:
			return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

		if zone:
			serializer = ZoneObdSerializer(zone)
			close_old_connections()
			return JsonResponse({'message':'Zone details', 'status':True, 'status_code':200, 'zone':serializer.data}, status=200)
		return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

	def put(self, request, id):
		if request.data:
			try:
				zone = ZoneObd.objects.filter(id=id).first()
				close_old_connections()
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

			update_zone_alert = self.check_update_fields(zone, request.data)
			print(update_zone_alert, 'update zone alerts too')
			if zone:
				serializer = ObdZoneUpdateSerializer(zone, data=request.data)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()

					if update_zone_alert:
						self.update_zone_alert_device(id)
					return JsonResponse({'message':'Zone Updated Successfully', 'status':True, 'status_code':204, 'zone':serializer.data}, status=200)
				return JsonResponse({'message':'Error While Updating Zone', 'status_code':400, 'status':False, 'errors':serializer.errors}, status=200)
			return JsonResponse({'message':'Invalid Zone selected', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False})

	def check_update_fields(self, old_data, new_data):
		try:
			if new_data.get('latitude'):
				if float(new_data.get('latitude')) != float(old_data.latitude):
					return True

			if new_data.get('longitude'):
				if float(new_data.get('longitude')) != float(old_data.longitude):
					return True

			if new_data.get('radius'):
				if float(new_data.get('radius')) != float(old_data.radius):
					return True
			return False
		except(Exception)as e:
			return False

	def delete(self, request, id):
		try:
			zone = ZoneObd.objects.filter(id=id).first()
		except(Exception)as e:
			return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

		if zone:
			zone_alert = ZoneAlertObd.objects.filter(zone=zone).all()
			if zone_alert:
				for alert in zone_alert:
					self.prepare_save_delete_alert(alert.imei, alert.zone_device_id)
				zone_alert.delete()
			zone.delete()
			close_old_connections()
			return JsonResponse({'message':'Zone Deleted Successfully', 'status':True, 'status_code':204}, status=200)
		return JsonResponse({'message':'Invalid Zone selected', 'status_code':404, 'status':False}, status=200)

	def update_zone_alert_device(self, id):
		alerts = ZoneAlertObd.objects.filter(zone=id).all()
		zone = ZoneObd.objects.filter(id=id).last()
		if zone:
			for alert in alerts:
				self.prepare_command(zone, alert.zone_device_id, alert.imei)
				alert.status = False
				alert.save()

	def prepare_command(self, zone, device_zone_id, imei):
		app_conf = AppConfiguration.objects.filter(key_name='zone_creation').last()

		imei_details = SimMapping.objects.filter(imei=imei).last()

		if imei_details:
			if imei_details.model:
				model = imei_details.model
			else:
				model = 'GV500'

			if zone.type == 'no-go':
				zone_types = 1
			elif zone.type == 'keep-in':
				zone_types = 2
			else:
				zone_types = 3

			lat = "{:.6f}".format(float(zone.latitude))
			longi = "{:.6f}".format(float(zone.longitude))

			if app_conf:
				message = app_conf.key_value
				message = message.replace('model', model)
				message = message.replace('gid', str(device_zone_id))
				message = message.replace('zone_types', str(zone_types))
				message = message.replace('longitude', str(longi))
				message = message.replace('latitude', str(lat))
				message = message.replace('radius', str(int(zone.radius)))
				self.save_command(imei, message)
			else:
				message = 'AT+GTGEO=model,gid,zone_types,longitude,latitude,radius,10,,,,,0,0,0,,FFFF$'
				message = message.replace('model', model)
				message = message.replace('gid', str(device_zone_id))
				message = message.replace('zone_types', str(zone_types))
				message = message.replace('longitude', str(longi))
				message = message.replace('latitude', str(lat))
				message = message.replace('radius', str(int(zone.radius)))
				self.save_command(imei, message)
		pass



	def save_command(self, imei, message):
		serializer = DeviceCommandsSerializer(data={'imei':imei, 'command':message})
		if serializer.is_valid():
			serializer.save()
		pass

	def prepare_save_delete_alert(self, imei, gid):
		app_conf = AppConfiguration.objects.filter(key_name='zone_deletion').last()
		self.get_imei_details(imei)
		if self.imei_details.model:
			model = self.imei_details.model
		else:
			model = 'gv500'

		if app_conf:
			message = app_conf.key_value
			message = message.replace('model', model)
			message = message.replace('gid', str(gid))
		else:
			message = 'AT+GTGEO=model,gid,0,,,,,,,,,0,0,1,,FFFF$'
			message = message.replace('model', model)
			message = message.replace('gid', str(gid))

		serializer = DeviceCommandsSerializer(data={'imei':imei, 'command':message})
		if serializer.is_valid():
			serializer.save()


	def get_imei_details(self, imei):
		sim_mapping = SimMapping.objects.filter(imei=imei).last()
		if sim_mapping:
			self.imei_details = sim_mapping
		else:
			self.imei_details = None



class ObdZoneAlertApiView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.zone_ids = [0,1,2,3,4]
		self.available_ids = []
		self.imei_details = None

	def post(self, request):
		imei = request.data.get('imei', None)
		customer_id = request.data.get('customer_id', None)
		zone = request.data.get('zone', None)

		self.get_imei_details(imei)
		if not self.imei_details:
			return JsonResponse({'message':'Invalid IMEI, Please check IMEI you sending', 'status':False, 'status_code':400}, status=200)

		if imei and customer_id:
			zone_alerts = ZoneAlertObd.objects.filter(imei=imei, customer_id=customer_id).all()
			if len(zone_alerts)<5:
				zone_que = ZoneObd.objects.filter(id=zone).last()
				if zone_que:

					self.get_available_ids(zone_alerts)
					self.prepare_command(zone_que)
					request.data['zone_device_id'] = self.available_ids[0]
					request.data['type'] = zone_que.type
					serializer = ZoneAlertObdSerializer(data=request.data)
					if serializer.is_valid():
						serializer.save()
						self.save_command(imei)
						return JsonResponse({'message':'Zone Alert Created Successfully. It will be activated shortly', 'status':True, 'status_code':200}, status=200)
					return JsonResponse({'message':'Error During Creating Zone Alert, Please try again letter', 'status':False, 'status_code':400, 'error':serializer.errors}, status=400)
				return JsonResponse({'message':"Invalid Zone, Please try again with valid zone", 'status':False, 'status_code':400}, status=200)
			return JsonResponse({'message':'Zone Alert Limit Exceeded', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'IMEI and Customer ID Required', 'status':False, 'status_code':400}, status=200)


	def get_imei_details(self, imei):
		sim_mapping = SimMapping.objects.filter(imei=imei).last()
		if sim_mapping:
			self.imei_details = sim_mapping
		else:
			self.imei_details = None


	def save_command(self, imei):
		serializer = DeviceCommandsSerializer(data={'imei':imei, 'command':self.message})
		if serializer.is_valid():
			serializer.save()
		pass


	def get_available_ids(self, zones):
		taken = []
		for zone in zones:
			if zone.zone_device_id in self.zone_ids:
				taken.append(zone.zone_device_id)
		self.available_ids = list(set(self.zone_ids) - set(taken))

	def prepare_command(self, zone):
		app_conf = AppConfiguration.objects.filter(key_name='zone_creation').last()
		if self.imei_details.model:
			model = self.imei_details.model
		else:
			model = 'gv500'

		if zone.type == 'no-go':
			zone_types = 1
		elif zone.type == 'keep-in':
			zone_types = 2
		else:
			zone_types = 3

		lat = "{:.6f}".format(float(zone.latitude))
		longi = "{:.6f}".format(float(zone.longitude))

		if app_conf:
			self.message = app_conf.key_value
			self.message = self.message.replace('model', model)
			self.message = self.message.replace('gid', str(self.available_ids[0]))
			self.message = self.message.replace('zone_types', str(zone_types))
			self.message = self.message.replace('longitude', str(longi))
			self.message = self.message.replace('latitude', str(lat))
			self.message = self.message.replace('radius', str(int(zone.radius)))
		else:
			self.message = 'AT+GTGEO=model,gid,zone_types,longitude,latitude,radius,10,,,,,0,0,0,,FFFF$'
			self.message = self.message.replace('model', model)
			self.message = self.message.replace('gid', str(self.available_ids[0]))
			self.message = self.message.replace('zone_types', str(zone_types))
			self.message = self.message.replace('longitude', str(longi))
			self.message = self.message.replace('latitude', str(lat))
			self.message = self.message.replace('radius', str(int(zone.radius)))


	def put(self, request):
		if request.data:
			alert_id = ZoneAlertObd.objects.filter(id=request.data.get('id', None)).last()
			if alert_id:
				serializer = ZoneAlertObdUpdateSerializer(alert_id, data=request.data)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({'message':'Zone alert updated successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'Error during updating zone alert, Please check the data you are sending', 'status':False, 'status_code':400}, status=400)
			return JsonResponse({'message':'Invalid zone alert', 'status':False, 'status_code':400}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)


	def delete(self, request):
		if request.data:
			alert_id = ZoneAlertObd.objects.filter(id=request.data.get('id', None)).last()
			if alert_id:
				self.prepare_save_delete_alert(alert_id.imei, alert_id.zone_device_id)
				alert_id.delete()

				return JsonResponse({'message':'Zone alert deleted successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid zone alert, please select valid zone alert', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)

	def prepare_save_delete_alert(self, imei, gid):
		app_conf = AppConfiguration.objects.filter(key_name='zone_deletion').last()
		self.get_imei_details(imei)
		if self.imei_details.model:
			model = self.imei_details.model
		else:
			model = 'gv500'

		if app_conf:
			message = app_conf.key_value
			message = message.replace('model', model)
			message = message.replace('gid', str(gid))
		else:
			message = 'AT+GTGEO=model,gid,0,,,,,,,,,0,0,1,,FFFF$'
			message = message.replace('model', model)
			message = message.replace('gid', str(gid))

		serializer = DeviceCommandsSerializer(data={'imei':imei, 'command':message})
		if serializer.is_valid():
			serializer.save()

	def get(self, request):
		# imei = request.GET.get('imei', None)
		customer_id = request.GET.get('customer_id', None)

		if customer_id:
			alert_id = ZoneAlertObd.objects.filter(customer_id=customer_id).all()
			serializer = ZoneAlertObdSerializer(alert_id, many=True)
			return JsonResponse({'message':'Zone Alert List', 'status':True, 'status_code':200, 'zone_alert':serializer.data}, status=200)
		return JsonResponse({'message':'IMEI and Customer ID required', 'status':False, 'status_code':400}, status=200)



class ZoneAlertAckApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			if request.data.get('protocol', None) == '+ACK:GTGEO':
				zone_alert = ZoneAlertObd.objects.filter(imei=request.data.get('imei', None), zone_device_id=request.data.get('geo_id', None)).last()
				if zone_alert:
					zone_alert.status = True
					zone_alert.save()
					return JsonResponse({'message':'Zone Alert Activated Successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'Invalid Zone Alert', 'status':False, 'status_code':400}, status=400)
			return JsonResponse({'message':'Invalid Data', 'status':False, 'status_code':200}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)