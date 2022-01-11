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


exclude_obd = [None, 0, 0.0]
time_fmt = '%Y-%m-%d %H:%M:%S'



class MongoDataDelete(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		# trips = UserTrip.objects.filter(customer_id=None).all()
		# print(trips.delete())
		noti = Notifications.objects.first()
		if noti:
			ser = NotificationsSerializer(noti).data
			serializer = NotificationsBackupSerializer(data={
				'customer_id' : ser.get('customer_id'),
				'title' : ser.get('title'),
				'body' : ser.get('body'),
				'imei' : ser.get('imei'),
				'type' : ser.get('type'),
				'record_date_timezone' : ser.get('record_date_timezone'),
				'longitude' : ser.get('longitude'),
				'latitude' : ser.get('latitude'),
				'alert_name' : ser.get('alert_name'),
				'event' : ser.get('event'),
				'battery_percentage' : ser.get('battery_percentage'),
				'location' : ser.get('location'),
				'speed' : ser.get('speed')
				})
			if serializer.is_valid():
				serializer.save()
			else:
				print(serializer.errors)
			pass
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)


class SubscriptionView(APIView):
	def post(self, request):
		if request.data:
			serializer = SubscriptionSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()
				return JsonResponse({'message':'Subscription Saved Successfully', 'status':True, 'status_code':201}, status=201)
			return JsonResponse({'message':'Invalid Data, Please Check', 'status':False, 'status_code':400 , 'errors':serializer.errors}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)


class SubscriptionDeviceListView(APIView):
    
	def getold(self, request, customer_id):
		driver_score = 100
		try:
			token_customer_id = customer_id
		except(Exception)as e:
			token_customer_id = None
		try:
			category = request.GET['category']
		except(Exception)as e:
			return JsonResponse({'message':'Category required!', 'status':False, 'status_code':400}, status=200)

		if customer_id == str(token_customer_id):
			category_list = self.get_device_categories(category)
			devices = Subscription.objects.filter(customer_id=customer_id, device_in_use=True, device_listing=True, device_model__in=category_list).all()
			if devices:
				serializer = DeviceListSerializer(devices, many=True)
				if category == 'obd':
					get_device_details_list = self.get_device_details(serializer.data)
					# driver_score = self.get_driver_score(customer_id)
					return JsonResponse({'message':'List of devices', 'devices':get_device_details_list, 'status':True, 'status_code':200, 'driver_score':driver_score}, status=200)
				elif category == 'gps':
					get_device_details_list = self.get_gps_device_details(serializer.data)
					return JsonResponse({'message':'List of devices', 'devices':get_device_details_list, 'status':True, 'status_code':200}, status=200)
				

			return JsonResponse({'message':'List of devices', 'devices':[], 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Unathorized Access', 'status':False, 'status_code':401}, status=401)

	permission_classes = (AllowAny,)
	def get(self, request, customer_id):
		driver_score = 100
		try:
			token_customer_id = customer_id
		except(Exception)as e:
			token_customer_id = None
		get_gps_device_details_list = []
		get_device_details_list= []
		if customer_id == str(token_customer_id):
			category = 'gps'
			category_list = self.get_device_categories(category)
			# print(category_list,'CATEGORY LIST')
			devices = Subscription.objects.filter(customer_id=customer_id, device_in_use=True, device_listing=True, device_model__in=category_list).all()
			# print(devices,'DEVICES')

			if devices:
				# print('Inside Devices')
				serializer = DeviceListSerializer(devices, many=True)				
				# print('Inside Devices2')
				get_gps_device_details_list = self.get_gps_device_details(serializer.data)
    
			category = 'obd'
			# print('OBD HERE')
			category_list = self.get_device_categories(category)
			# print(category_list,'category? obd')
			devices = Subscription.objects.filter(customer_id=customer_id, device_in_use=True, device_listing=True, device_model__in=category_list).all()
			# print(devices,'DEVICES OBD')
			if devices:
				serializer = DeviceListSerializer(devices, many=True)				
				get_device_details_list = self.get_device_details(serializer.data)
			return JsonResponse({'message':'List of both devices','obd_device':get_device_details_list,'gps_device':get_gps_device_details_list,'status':True,'status_code':200},status=200)

			return JsonResponse({'message':'List of devices', 'devices':[], 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Unathorized Access', 'status':False, 'status_code':401}, status=401)



	def get_driver_score(self, imei):
		if imei:
			driver_score = DriverScore.objects.filter(imei=imei).last()
			if driver_score:
				return driver_score.driver_score
			return 100
		return 100

	def get_gps_device_details(self, devices): 
		device_details = []

		for device in devices:
			fri_markers = GLFriMarkers.objects.filter(imei=device.get('imei_no', None)).last()
			if fri_markers:
				serializer = GLFriMarkersSerializer(fri_markers)
				device['device_details'] = serializer.data
				device['last_reported'] = self.get_last_reported_gps(device.get('imei_no', None))
				device['device_details']['trip_running'] = self.get_device_moving_gps(device.get('imei_no', None))
			else:
				device['device_details'] = {}
			device_details.append(device)
		return device_details

	def get_device_details(self, devices):
		device_details = []
		for device in devices:
			obd_details = ObdMarkers.objects.filter(imei=device['imei_no'], engine_rpm__isnull = False, engine_coolant_temp__isnull = False, fuel_consumption__isnull = False, throttle_position__isnull = False, engine_load__isnull = False, longitude__isnull=False, latitude__isnull=False).filter(~queue(fuel_consumption__in=['nan', 'null'])).last()
			if obd_details:
				serializer = DeviceObdMarkersSerializer(obd_details)
				device['device_details'] = serializer.data
				device['device_details']['device_status'] = self.get_device_status(device['imei_no']) 
				device['device_details']['trip_running'] = self.get_device_moving_obd(device['imei_no'])
				device['last_reported'] = self.get_last_reported_obd(device['imei_no'])
				device['driver_score'] = self.get_driver_score(device['imei_no'])
			else:
				obd_details = ObdMarkers.objects.filter(imei=device['imei_no'], longitude__isnull=False, latitude__isnull=False).last()
				if obd_details:
					serializer = DeviceObdMarkersSerializer(obd_details)
					device['device_details'] = serializer.data
					device['device_details']['trip_running'] = self.get_device_moving_obd(device['imei_no'])
				else:
					device['device_details'] = {}
					device['device_details']['trip_running'] = self.get_device_moving_obd(device['imei_no'])
				device['driver_score'] = self.get_driver_score(device['imei_no'])
			device_details.append(device)
		return device_details

	def get_last_reported_obd(self, imei):
		last_obd = ObdMarkers.objects.filter(imei=imei).last()
		serializer = DeviceObdMarkersSerializer(last_obd)
		return serializer.data


	def get_last_reported_gps(self, imei):
		last_obd = GLFriMarkers.objects.filter(imei=imei).last()
		serializer = GLFriMarkersSerializer(last_obd)
		return serializer.data

	def get_device_status(self, imei):
		fri_details = FriMarkers.objects.filter(imei=imei, device_status__isnull=False).last()
		if fri_details:
			return fri_details.device_status
		return None


	def get_device_categories(self, category):
		# print(category)
		categories = SimMapping.objects.filter(category=category).values('model').distinct()
		print(categories,'Categories')
		# print(categories,'Categories')
		category_list = [i.get('model') for i in categories]
		return category_list

	def get_device_moving_gps(self, imei):
		stt_marker = SttMarkers.objects.filter(imei=imei).last()
		if stt_marker:
			if stt_marker.state == 42:
				gl_marker = GLFriMarkers.objects.filter(imei=imei).last()
				if gl_marker:
					time_diff = (
						time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
		                time.mktime(time.strptime(datetime.datetime.strftime(gl_marker.record_date, time_fmt), time_fmt))
		                )
					if((time_diff/60)<1):
						return True
				else:
					time_diff = (
						time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
		                time.mktime(time.strptime(datetime.datetime.strftime(stt_marker.record_date, time_fmt), time_fmt))
		                )
					if((time_diff/60)<1):
						return True
				return False
			return False
		return False


	def get_device_moving_obd(self, imei):
		
		last_obd = ObdMarkers.objects.filter(imei=imei).last()

		if last_obd:
			if last_obd.device_status == 'engine_start':
				time_diff = (
					time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
					time.mktime(time.strptime(datetime.datetime.strftime(last_obd.record_date, time_fmt), time_fmt))
					)

				if((time_diff/60)<2):
					# self.running_from = get_location(str(gtign.longitude), str(gtign.latitude))
					return True
				return False
			return False
		return False






class ZoneGroupView(APIView):
    
	permission_classes = (AllowAny,)
	def post(self, request, customer_id):
		if request.data:
			request.data['created_by'] = customer_id
			zone_id = request.data.get('zone')
			serializer = ZoneGroupWriteSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				if zone_id:
					zone = Zones.objects.filter(id=zone_id).first()
					zone.zone_group = ZoneGroup.objects.filter(id=serializer.data['id']).first()
					zone.save()
					close_old_connections()
				return JsonResponse({'message':'Zone Group Created Successfully', 'status_code':201, 'status':True, 'zone_group':serializer.data}, status=201)
			return JsonResponse({'message':'Error while creating zone group', 'status_code':400, 'status':False, 'errors':serializer.errors}, status=200)
		return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False})

	def get(self, request, customer_id):
		zone_group = ZoneGroup.objects.filter(created_by=customer_id).all()
		if zone_group:
			serializer = ZoneGroupReadSerializer(zone_group, many=True)
			return JsonResponse({'message':'Zone group listing successfull', 'status':True, 'status_code':200, 'zone_group':serializer.data}, status=200)
		return JsonResponse({'message':'Zone group listing successfull', 'status':True, 'status_code':200, 'zone_group':[]}, status=200)


class ZoneGroupIndividualView(APIView):
	def get(self, request, id):
		try:
			zone_group = ZoneGroup.objects.filter(id=id).first()
			close_old_connections()
		except(Exception)as e:
			return JsonResponse({'message':'Invalid Zone Group', 'status_code':404, 'status':False}, status=200)
		if zone_group:
			serializer = ZoneGroupReadSerializer(zone_group)
			return JsonResponse({'message':'Zone Group details', 'status':True, 'status_code':200, 'zone_group':serializer.data}, status=200)
		return JsonResponse({'message':'Invalid Zone Group', 'status_code':404, 'status':False}, status=200)

	def put(self, request, id):
		if request.data:
			try:
				zone_group = ZoneGroup.objects.filter(id=id).first()
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Zone Group', 'status_code':404, 'status':False}, status=200)

			if zone_group:
				serializer = ZoneGroupUpdateSerializer(zone_group, data=request.data)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
					return JsonResponse({'message':'Zone Group Updated Successfully', 'status':True, 'status_code':204, 'zone_group':serializer.data}, status=200)
				return JsonResponse({'message':'Error while Updating code', 'status_code':400, 'status':False, 'errors':serializer.errors}, status=200)
			return JsonResponse({'message':'Invalid Zone Group selected', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False})

	def delete(self, request, id):
		try:
			zone_group = ZoneGroup.objects.filter(id=id).first()
		except(Exception)as e:
			return JsonResponse({'message':'Invalid Zone Group', 'status_code':404, 'status':False}, status=200)

		if zone_group:
			zone_group.delete()
			return JsonResponse({'message':'Zone Group Deleted Successfully', 'status':True, 'status_code':204}, status=200)
		return JsonResponse({'message':'Invalid Zone Group selected', 'status_code':404, 'status':False}, status=200)


class ZoneView(APIView):
	def post(self, request, customer_id):
		if request.data:
			request.data['customer_id'] = customer_id
			serializer = ZoneWriteSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()
				return JsonResponse({'message':'Zone Created Successfully', 'status_code':201, 'status':True, 'zone':serializer.data}, status=201)
			return JsonResponse({'message':'Error while creating zone', 'status_code':400, 'status':False, 'errors':serializer.errors}, status=200)
		return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False})
				

	def get(self, request, customer_id):
		zone = Zones.objects.filter(customer_id=customer_id).all()
		if zone:
			serializer = ZoneReadSerializer(zone, many=True)
			return JsonResponse({'message':'Zone list successfull', 'status':True, 'status_code':200, 'zone':serializer.data}, status=200)
		return JsonResponse({'message':'List of zones', 'status':True, 'status_code':200, 'zone':[]}, status=200)

class GpsObdZoneView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request, customer_id):
		if request.data:
			request.data['customer_id'] = customer_id
			gps_serializer = ZoneWriteSerializer(data=request.data)
			obd_serializer = ZoneObdSerializer(data=request.data)
			if gps_serializer.is_valid() & obd_serializer.is_valid():
				gps_serializer.save()
				obd_serializer.save()
				return JsonResponse({'message':'Zone Created Successfully', 'status_code':201, 'status':True, 'gps_zone':gps_serializer.data,'obd_zone':obd_serializer.data}, status=201)
			elif gps_serializer.is_valid():
				gps_serializer.save()
				return JsonResponse({'message':'Zone Created Successfully', 'status_code':201, 'status':True, 'zone':gps_serializer.data}, status=201)
			elif obd_serializer.is_valid():
				obd_serializer.save()
				return JsonResponse({'message':'Zone OBD Created Successfully', 'status':True, 'status_code':200, 'zone':obd_serializer.data}, status=200)
			return JsonResponse({'message':'Error while creating zone', 'status_code':400, 'status':False, 'errors':serializer.errors}, status=200)
		return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False})
				

	def get(self, request, customer_id):
		gps_zone = Zones.objects.filter(customer_id=customer_id).all()
		obd_zone = ZoneObd.objects.filter(customer_id=customer_id).all()		
		if len(gps_zone)!=0 and len(obd_zone)!=0:
			gps_serializer = ZoneReadSerializer(gps_zone, many=True)
			obd_serializer = ZoneObdSerializer(obd_zone, many=True)
			return JsonResponse({'message':'Zone list successfull', 'status':True, 'status_code':200, 'gps_zone':gps_serializer.data,'obd_zone':obd_serializer.data}, status=200)
		elif len(gps_zone)!=0:
			# print('IN GPS ZONE')
			gps_serializer = ZoneReadSerializer(gps_zone, many=True)
			return JsonResponse({'message':'Zone list successfull', 'status':True, 'status_code':200, 'gps_zone':gps_serializer.data}, status=200)
		elif len(obd_zone)!=0:
			obd_serializer = ZoneObdSerializer(obd_zone, many=True)
			return JsonResponse({'message':'Zone list successfull', 'status':True, 'status_code':200, 'zone':serializer.data}, status=200)
		return JsonResponse({'message':'List of zones', 'status':False, 'status_code':400, 'zone':[]}, status=200)



    
			    

class ZoneIndividualView(APIView):
	def get(self, request, id):
		try:
			zone = Zones.objects.filter(id=id).first()
			close_old_connections()
		except(Exception)as e:
			return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

		if zone:
			serializer = ZoneReadSerializer(zone)
			close_old_connections()
			return JsonResponse({'message':'Zone details', 'status':True, 'status_code':200, 'zone':serializer.data}, status=200)
		return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

	def put(self, request, id):
		if request.data:
			try:
				zone = Zones.objects.filter(id=id).first()
				close_old_connections()
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

			if zone:
				serializer = ZoneUpdateSerializer(zone, data=request.data)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
					return JsonResponse({'message':'Zone Updated Successfully', 'status':True, 'status_code':204, 'zone':serializer.data}, status=200)
				return JsonResponse({'message':'Error While Updating Zone', 'status_code':400, 'status':False, 'errors':serializer.errors}, status=200)
			return JsonResponse({'message':'Invalid Zone selected', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False})

	def delete(self, request, id):
		try:
			zone = Zones.objects.filter(id=id).first()
		except(Exception)as e:
			return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)

		if zone:
			zone_alert = ZoneAlert.objects.filter(zone=zone).all()
			if zone_alert:
				zone_alert.delete()
			zone.delete()
			close_old_connections()
			return JsonResponse({'message':'Zone Deleted Successfully', 'status':True, 'status_code':204}, status=200)
		return JsonResponse({'message':'Invalid Zone selected', 'status_code':404, 'status':False}, status=200)


class NotificationSenderView(APIView):
	def post(self, request):
		if request.data:
			notification = NoticationSender.objects.filter(customer_id=request.data.get('customer_id', None), category=request.data.get('category', None)).first()
			if notification:
				serializer = NotificationSenderSerializer(notification, data=request.data)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
					return JsonResponse({'message':'Token Saved Successfully', 'status':True, 'status_code':201}, status=200)
				return JsonResponse({'message':'Invalid Data', 'status':False, 'status_code':400, 'error':serializer.errors}, status=200)
			else:
				serializer = NotificationSenderSerializer(data=request.data)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
					return JsonResponse({'message':'Token Saved Successfully', 'status':True, 'status_code':201}, status=200)
				return JsonResponse({'message':'Invalid Data', 'status':False, 'status_code':400, 'error':serializer.errors}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)


class NotificationTokenRemovalView(APIView):
	def post(self, request):
		if request.data:
			notification = NoticationSender.objects.filter(customer_id=request.data.get('customer_id', None), category=request.data.get('category', None)).first()
			if notification:
				serializer = NotificationSenderSerializer(notification, data=request.data)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({'message':'Token Removed successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'Invalid Data', 'status':True, 'status_code':200, 'error':serializer.errors}, status=200)
			return JsonResponse({'message':'Notification token, not found', 'status_code':200, 'status':True}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':True, 'status_code':200}, status=200)



class ReportView(APIView):
	def get(self, request, customer_id, imei):
		request_from_date = request.GET.get('from', None)
		request_to_date = request.GET.get('to', None)
		request_date = request.GET.get('date', None)

		# if imei:
		# 	reports = Reports.objects.filter(imei=imei).all()
		# 	print(reports)
		# 	serializer = ReportsSerializer(reports, many=True)
		# 	return JsonResponse({'message':'Reports of your device', 'status':True, 'status_code':200, 'reports':serializer.data}, status=200)

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')
			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				reports = Reports.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all()
				serializer = ReportsSerializer(reports, many=True)
				close_old_connections()
				return JsonResponse({'message':'Reports of your device', 'from_date':request_from_date, 'to_date':request_to_date, 'reports':serializer.data, 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				reports = Reports.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all()
				serializer = ReportsSerializer(reports, many=True)
				close_old_connections()
				return JsonResponse({'message':'Reports of your device', 'from_date':request_date, 'to_date':request_date, 'reports':serializer.data, 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_date, 'to_date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'reports':[]}, status=200)



import requests
class LocationView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, lng, lat):
		# check_location = Location.objects.filter(longitude=lng, latitude=lat).first()
		
		# if check_location:
		# 	serializer = LocationSerializer(check_location)
		# 	return JsonResponse({'message':'Retreiving location successfull', 'status_code':200, 'status':True, 'location':serializer.data, 'from':'db'}, status=200)
		
		check_location = requests.get('https://amcrestgpstracker.com/manage_gps/fetchlocation.php?lat={0}&long={1}'.format(lat, lng))
		
		if check_location.text != 'NONE':
			location = {
				"longitude":str(lng),
				"latitude" : str(lat),
				"location_name" : str(check_location.text)
			}
			return JsonResponse({'message':'Retreiving location successfull', 'status_code':200, 'status':True, 'location':location, 'from':'db'}, status=200)
		else:
			response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng=+"+lat+","+lng+"&key="+self.get_google_keys())
			location_to_send = json.loads(response.text)
			try:
				location_to_send = location_to_send.get('results', None)[0]
				location_to_send = location_to_send.get('formatted_address', None)
				# self.save_location(lat, lng, location_to_send)
			except(Exception)as e:
				print(e)
				location_to_send = None
			close_old_connections()
			if location_to_send:
				location_obj = {
						"longitude":lng,
						"latitude" : lat,
						"location_name" : location_to_send
					}
				return JsonResponse({'message':'Retreiving location successfull', 'status_code':200, 'status':True, 'location':location_obj}, status=200)
			return JsonResponse({'message':'Unable to find location', 'status_code':404, 'status':False, 'location':{}}, status=200)



	def save_location(self, lat, lng, address):
		location_obj = {
			"longitude":str(lng),
			"latitude" : str(lat),
			"location_name" : str(address)
		}
		serializer = LocationSerializer(data=location_obj)
		if serializer.is_valid():
			serializer.save()
			close_old_connections()

	def get_google_keys(self):
		google_key = GoogleMapAPIKey.objects.first()
		if google_key:
			return str(google_key.key)
		return str(settings.GOOGLE_MAP_KEY)


class GlobalLocationView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, lng, lat):
		api_key = request.GET.get('location_api_key', None)
		if api_key:
			validate = AppConfiguration.objects.filter(key_name='location_api_key').last()
			if validate.key_value == api_key:
				check_location = Location.objects.filter(longitude=lng, latitude=lat).first()
				if check_location:
					serializer = LocationSerializer(check_location)
					return JsonResponse({'message':'Retreiving location successfull', 'status_code':200, 'status':True, 'location':serializer.data}, status=200)
				# check_location = requests.get('https://amcrestgpstracker.com/manage_gps/fetchlocation.php?lat={0}&long={1}'.format(lat, lng))
				# if check_location.text != 'NONE':
				# 	location = {
				# 		"longitude":str(lng),
				# 		"latitude" : str(lat),
				# 		"location_name" : str(check_location.text)
				# 	}
				# 	return JsonResponse({'message':'Retreiving location successfull', 'status_code':200, 'status':True, 'location':location, 'from':'db'}, status=200)
				else:
					response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng=+"+lat+","+lng+"&key="+self.get_google_keys())
					location_to_send = json.loads(response.text)
					try:
						location_to_send = location_to_send.get('results', None)[0]
						location_to_send = location_to_send.get('formatted_address', None)
						self.save_location(lat, lng, location_to_send)
					except(Exception)as e:
						location_to_send = None
					close_old_connections()
					if location_to_send:
						location_obj = {
								"longitude":lng,
								"latitude" : lat,
								"location_name" : location_to_send
							}
						return JsonResponse({'message':'Retreiving location successfull', 'status_code':200, 'status':True, 'location':location_obj}, status=200)
					return JsonResponse({'message':'Unable to find location', 'status_code':404, 'status':False, 'location':{}}, status=200)
			return JsonResponse({'message':'Unauthorized Access', 'status':False, 'status_code':401}, status=401)
		return JsonResponse({'message':'Unauthorized Access', 'status':False, 'status_code':401}, status=401)



	def save_location(self, lat, lng, address):
		location_obj = {
			"longitude":str(lng),
			"latitude" : str(lat),
			"location_name" : str(address)
		}
		serializer = LocationSerializer(data=location_obj)
		if serializer.is_valid():
			serializer.save()
			close_old_connections()
		# main_location_machine.save_location(location_obj)
		# loop = asyncio.new_event_loop()
		# loop.run_in_executor(None, main_location_machine.save_location, [location_obj])
		# from app.events.main_location_machine import save_location
		# import _thread
		# _thread.start_new_thread(save_location, (location_obj,))

	def get_google_keys(self):
		google_key = GoogleMapAPIKey.objects.first()
		if google_key:
			return str(google_key.key)
		return str(settings.GOOGLE_MAP_KEY)


class LocationInsertView(APIView):
	def post(self, request):
		if request.data:
			serializer = LocationSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return JsonResponse({'message':'Location added successfully', 'status':True, 'status_code':201}, status=200)
			return JsonResponse({'message':'Invalid Data', 'status':False, 'status_code':400, 'error':serializer.errors}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)




class VehicleIdleView(APIView):
	def get(self, request, imei):
		# +RESP:GTIGF
		engine_start = IgnitionOnoff.objects.filter(protocol='+RESP:GTIGN', imei=imei).last()
		engine_start_serializer = IgnitionOnoffSerializer(engine_start)
		engine_stop = IgnitionOnoff.objects.filter(protocol='+RESP:GTIGF', imei=imei).last()
		engine_stop_serializer = IgnitionOnoffSerializer(engine_stop)
		close_old_connections()
		return JsonResponse({'message':'Last Ignition On and Off report', 'engine_start':engine_start_serializer.data, 'engine_stop': engine_stop_serializer.data, 'status':True, 'status_code':200}, status=200)

class EngineSummaryView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		engine_summary = EngineSummary.objects.filter(imei=imei).last()
		close_old_connections()
		if engine_summary:
			serializer = EngineSummarySerializer(engine_summary)
			return JsonResponse({'message':'Engine Summary', 'status':True, 'status_code':200, 'engine_summary':serializer.data}, status=200)
		return JsonResponse({'message':'Engine Summary not found', 'status':False, 'status_code':200, 'engine_summary':{}}, status=200)


	def post(self, request, imei):
		trip_dates = request.data.get('trip_dates', None)
		result_to_be_send = []
		idle_time_list = []
		idle_time_records = []
		if trip_dates:
			for date in trip_dates:
				result = self.get_engine_summary(date, imei)
				result_to_be_send.append(result)
				idle_time_list.append(self.idle_time(date, imei))
				idle_time_records.append(self.get_engine_summary_records(date, imei))
			return JsonResponse({'message':'Engine Summary', 'status':True, 'status_code':200, 'engine_summary':result_to_be_send, 'idle_time':idle_time_list, 'idle_records':idle_time_records}, status=200)
		return JsonResponse({'message':'trip dated required to filter', 'status':False, 'status_code':400}, status=200)


	def idle_time(self, date, imei):
		start_idle_records = IdleDevice.objects.filter(send_time__lt=date.get('end', None), send_time__gt=date.get('start', None), protocol='+RESP:GTIDN', imei=imei).all()
		end_idle_records = IdleDevice.objects.filter(send_time__lt=date.get('end', None), send_time__gt=date.get('start', None), protocol='+RESP:GTIDF', imei=imei).all()
		
		total_time = 0
		for i in range(len(start_idle_records)):

			try:
				start_time = start_idle_records[len(start_idle_records)-1]
				end_time = end_idle_records[len(end_idle_records)-1]
			except(Exception)as e:
				pass

			try:
				new_time = str(end_time.send_time)
				old_time = str(start_time.send_time)
			except(Exception)as e:
				pass

			try:
				time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
	                time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
			except(Exception)as e:
				time_diff = 0

			total_time = total_time+time_diff
		return total_time

	def get_engine_summary_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

	def get_engine_summary(self, trip_date, imei):
		start = trip_date.get('start', None)
		end = trip_date.get('end', None)
		if start and end:
			try:
				engine_summary = EngineSummary.objects.filter(imei=imei, send_time__lte=end, send_time__gte=start).last()
				close_old_connections()
				if engine_summary:
					serializer = EngineSummarySerializer(engine_summary)
					return serializer.data
				else:
					engine_summary = EngineSummary.objects.filter(imei=imei, send_time__lte=end).last()
					if engine_summary:
						serializer = EngineSummarySerializer(engine_summary)
						return serializer.data
					else:
						engine_summary = EngineSummary.objects.filter(imei=imei, send_time__gte=start).first()
						if engine_summary:
							serializer = EngineSummarySerializer(engine_summary)
							return serializer.data
						else:
							return {}
				return {}
			except(Exception)as e:
				return {}
		return {}


	def prepare_date_object(self, date):
		date = str(date)
		try:
			date_time_fmt = '%Y-%m-%d %H:%M:%S'
			date_time = datetime.datetime.strptime(date[:4]+'-'+date[4:6]+'-'+date[6:8]+' '+date[-6:-4]+':'+date[-4:-2]+':'+date[-2:], date_time_fmt)
			return date_time
		except(Exception)as e:
			return None

from services.sim_message_sender import *
class UpdateOdometerView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.imei = None
		self.odometer = None
		self.message = None

	def post(self, request):
		self.imei = request.data.get('imei', None)
		self.odometer = request.data.get('odometer_value', None)
		self.category = self.get_category()
		# self.unit = request.data.get('unit', 'km')

		# if self.unit == 'miles':
		# 	self.odometer = str(float(self.odometer)*1.60934)


		if self.imei and self.odometer:
			subscription_instance = Subscription.objects.filter(imei_no=self.imei).last()
			if subscription_instance:
				if subscription_instance.device_model:
					if self.prepare_message(subscription_instance.device_model):
						try:
							if message_receiver(self.imei, self.message):
								return JsonResponse({'message':'Requested to update odometer', 'status':True, 'status_code':200}, status=200)
							self.send_error_mail()
							return JsonResponse({'message':'Requested to update odometer, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
						except(Exception)as e:
							self.send_error_mail()
							return JsonResponse({'message':'Requested to update odometer, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
					self.send_error_mail()
					return JsonResponse({'message':'Requested to update odometer, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
				self.send_error_mail()
				return JsonResponse({'message':'Requested to update odometer, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid IMEI', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'IMEI and Odometer required', 'status':False, 'status_code':400}, status=200) 



	def prepare_message(self, model):
		if self.category == 'gps':
			message = AppConfiguration.objects.filter(key_name = 'odometer_message_gps').first()
		elif self.category == 'obd':
			message = AppConfiguration.objects.filter(key_name = 'odometer_message_obd').first()
		else:
			message = None
		close_old_connections()

		if message:
			message = message.key_value.replace('mileage', self.odometer)
			self.message = message.replace('model', model)
			return True
		self.message = 'Couldn\'t find message in App configurations.'
		return False

	def send_error_mail(self):
		sim_iccid = SimMapping.objects.filter(imei=self.imei).first()
		close_old_connections()
		if sim_iccid:
			subject = 'Error during sending message to update Odometer, please look into the server and admin configuration table.'
			content = 'iccid :'+sim_iccid.iccid+',\n\nIMEI : '+self.imei+',\n\nMessage : '+self.message
			send_error_mail(subject, content)

	def get_category(self):
		sim_mapping = SimMapping.objects.filter(imei=self.imei).last()
		if sim_mapping:
			return sim_mapping.category
		return None




class DeviceRebootView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.imei = None
		self.odometer = None
		self.message = None
		self.model = None

	def post(self, request):
		self.imei = request.data.get('imei', None)
		self.category = self.get_category()
		# self.unit = request.data.get('unit', 'km')

		# if self.unit == 'miles':
		# 	self.odometer = str(float(self.odometer)*1.60934)

		if self.imei:
			subscription_instance = Subscription.objects.filter(imei_no=self.imei).last()
			if subscription_instance:
				if subscription_instance.device_model:

					if self.prepare_message(subscription_instance.device_model):
						try:
							if message_receiver_reboot(self.imei, self.message):
								return JsonResponse({'message':'Requested for reboot device', 'status':True, 'status_code':200}, status=200)
							self.send_error_mail()
							return JsonResponse({'message':'Requested for reboot device' , 'status':True, 'status_code':200}, status=200)
						except(Exception)as e:
							print(e)
							self.send_error_mail()
							return JsonResponse({'message':'Requested for reboot device' , 'status':True, 'status_code':200}, status=200)
					self.send_error_mail()
					return JsonResponse({'message':'Requested for reboot device' , 'status':True, 'status_code':200}, status=200)
				self.send_error_mail()
				return JsonResponse({'message':'Requested for reboot device' , 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid IMEI', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'IMEI and Odometer required', 'status':False, 'status_code':400}, status=200) 



	def prepare_message(self, model):
		message = AppConfiguration.objects.filter(key_name = 'reboot_'+model).first()
		if message:
			message = message.key_value.replace('model', model)
			self.message = message.replace('model', model)
			return True
		self.message = 'Couldn\'t find message in App configurations.'
		return False

	def send_error_mail(self):
		sim_iccid = SimMapping.objects.filter(imei=self.imei).first()
		close_old_connections()
		if sim_iccid:
			subject = 'Error during sending message to reboot device, please look into the server and admin configuration table.'
			content = 'iccid :'+sim_iccid.iccid+',\n\nIMEI : '+self.imei+',\n\nMessage : '+self.message
			send_error_mail(subject, content)

	def get_category(self):
		sim_mapping = SimMapping.objects.filter(imei=self.imei).last()
		if sim_mapping:
			self.model = sim_mapping.model
			return sim_mapping.category
		return None




class DeviceLiveLocationView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.imei = None
		self.message = None
		self.model = None

	def post(self, request):
		self.imei = request.data.get('imei', None)
		self.category = self.get_category()
		
		if self.imei:

			subscription_instance = Subscription.objects.filter(imei_no=self.imei).last()
			if subscription_instance:
				if subscription_instance.device_model:
					if self.prepare_message(subscription_instance.device_model):
						try:
							if message_receiver_reboot(self.imei, self.message):
								return JsonResponse({'message':'Requested for Live location', 'status':True, 'status_code':200}, status=200)
							self.send_error_mail()
							return JsonResponse({'message':'Requested for live location' , 'status':True, 'status_code':200}, status=200)
						except(Exception)as e:
							print(e)
							self.send_error_mail()
							return JsonResponse({'message':'Requested for live location' , 'status':True, 'status_code':200}, status=200)
					self.send_error_mail()
					return JsonResponse({'message':'Requested for live location' , 'status':True, 'status_code':200}, status=200)
				self.send_error_mail()
				return JsonResponse({'message':'Requested for live location' , 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid IMEI', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'IMEI required', 'status':False, 'status_code':400}, status=200) 



	def prepare_message(self, model):
		message = AppConfiguration.objects.filter(key_name = 'live_location_'+model).first()
		
		if message:
			message = message.key_value.replace('model', model)
			self.message = message.replace('model', model)
			return True
		self.message = 'Couldn\'t find message in App configurations.'
		return False

	def send_error_mail(self):
		sim_iccid = SimMapping.objects.filter(imei=self.imei).first()
		close_old_connections()
		if sim_iccid:
			subject = 'Error during sending message to get live location, please look into the server and admin configuration table.'
			content = 'iccid :'+sim_iccid.iccid+',\n\nIMEI : '+self.imei+',\n\nMessage : '+self.message
			send_error_mail(subject, content)

	def get_category(self):
		sim_mapping = SimMapping.objects.filter(imei=self.imei).last()
		if sim_mapping:
			self.model = sim_mapping.model
			return sim_mapping.category
		return None



class GetSmsCount(APIView):
	def get(self, request, imei):
		sms_log = SmsLog.objects.filter(imei=imei).all()
		close_old_connections()
		serializer = SmsLogSerializer(sms_log, many=True)
		return JsonResponse({'message':'SMS log Retreived successfully', 'status':True, 'status_code':200, 'sms_log':serializer.data, 'count':len(serializer.data)}, status=200)


class 	MapSettingsUpdate(APIView):
	def put(self, request):
		cust = request.data.get('customer_id', None)
		if cust:
			map_setings = MapSettings.objects.filter(customer_id=cust).last()
			if map_setings:
				serializer = MapSettingsSerializer(map_setings, data=request.data)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({'message':'Updated Map Settings', 'status':True, 'status_code':200, 'map_setting':serializer.data}, status=200)
				return JsonResponse({'message':'Error during updating map settings', 'status_code':200, 'status':False, 'error':serializer.errors}, status=200)
			else:
				serializer = MapSettingsSerializer(data=request.data)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({'message':'Saved Map settings', 'status_code':200, 'status':True, 'map_setting':serializer.data}, status=200)
				return JsonResponse({'message':'Error during updating map settings', 'status_code':200, 'status':False}, status=200)
		return JsonResponse({'message':'Customer ID required', 'status_code':200, 'status':False, 'error':serializer.errors}, status=200)






class CancelledDeviceListView(APIView):
    # permission_classes = (AllowAny,)
    def get(self, request, customer_id):
        user = User.objects.filter(customer_id=customer_id, subuser=False).first()
        # category = request.GET.get('category')
        if user:
			# Gps Cancelled Device List
            gps_category_list = self.get_device_categories('gps')
            devices = Subscription.objects.filter(customer_id=customer_id, device_listing=False, device_in_use=True, device_model__in=gps_category_list).all()
            gps_serializer = SubscriptionInactiveDeviceSerializer(devices, many=True)
            gps_user_serializer = UserInfoSerializer(user)
			# Obd Cancelled Device List
            obd_category_list = self.get_device_categories('obd')
            devices = Subscription.objects.filter(customer_id=customer_id, device_listing=False, device_in_use=True, device_model__in=obd_category_list).all()
            obd_serializer = SubscriptionInactiveDeviceSerializer(devices, many=True)
            obd_user_serializer = UserInfoSerializer(user)
            return JsonResponse({'message':'inactive Devices', 'status_code':200, 'status':True,'gps':{ 'gps_devices':gps_serializer.data, 'gps_user_details':gps_user_serializer.data},'obd':{ 'obd_devices':obd_serializer.data, 'obd_user_details':obd_user_serializer.data}})
        return JsonResponse({'message':'Invalid Customer Id, cannot find user', 'status_code':404})

    
    def get_device_categories(self, category):
        categories = SimMapping.objects.filter(category=category).values('model').distinct()
        category_list = [i.get('model') for i in categories]
        return category_list




class UpdateSpeedView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.imei = None
		self.odometer = None
		self.message = None

	def post(self, request):
		self.imei = request.data.get('imei', None)
		self.speed = request.data.get('speed', None)
		self.category = self.get_category()
		# self.unit = request.data.get('unit', 'km')

		# if self.unit == 'miles':
		# 	self.odometer = str(float(self.odometer)*1.60934)

		if self.imei and self.speed:
			subscription_instance = Subscription.objects.filter(imei_no=self.imei).last()
			if subscription_instance:
				if subscription_instance.device_model:
					if self.prepare_message(subscription_instance.device_model):
						try:
							if self.save_message():
								print('changin speed')
								self.update_speed()
								print('changin speed')
								return JsonResponse({'message':'Requested to update speed', 'status':True, 'status_code':200}, status=200)
							self.send_error_mail()
							return JsonResponse({'message':'Requested to update speed, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
						except(Exception)as e:
							print(e)
							self.send_error_mail()
							return JsonResponse({'message':'Requested to update speed, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
					self.send_error_mail()
					return JsonResponse({'message':'Requested to update speed, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
				self.send_error_mail()
				return JsonResponse({'message':'Requested to update speed, changes will be done shortly.' , 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid IMEI', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'IMEI and speed required', 'status':False, 'status_code':400}, status=200)

	def update_speed(self):
		setting = SettingsModel.objects.filter(imei=self.imei).last()
		if setting:
			setting.speed_limit = self.speed
			setting.save()
			print('saved')
			pass

	def save_message(self):
		serializer = DeviceCommandsSerializer(data={'imei':self.imei, 'command':self.message})
		if serializer.is_valid():
			serializer.save()
			return True
		else:
			return False

	def prepare_message(self, model):
		if self.category == 'gps':
			message = AppConfiguration.objects.filter(key_name = 'speed_message_gps').first()
		elif self.category == 'obd':
			message = AppConfiguration.objects.filter(key_name = 'speed_message_obd').first()
		else:
			message = None
		close_old_connections()

		if message:
			message = message.key_value.replace('speed', str(self.speed))
			self.message = message.replace('model', model)
			self.message = self.message.replace('imei', self.imei)
			return True
		self.message = 'Couldn\'t find message in App configurations.'
		return False

	def send_error_mail(self):
		sim_iccid = SimMapping.objects.filter(imei=self.imei).first()
		close_old_connections()
		if sim_iccid:
			subject = 'Error during sending message to speed, please look into the server and admin configuration table.'
			content = 'iccid :'+sim_iccid.iccid+',\n\nIMEI : '+self.imei+',\n\nMessage : '+self.message
			send_error_mail(subject, content)

	def get_category(self):
		sim_mapping = SimMapping.objects.filter(imei=self.imei).last()
		if sim_mapping:
			return sim_mapping.category
		return None