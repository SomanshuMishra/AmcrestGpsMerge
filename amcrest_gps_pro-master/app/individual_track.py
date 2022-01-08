import hashlib

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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import datetime

from .serializers import *
from .models import *

from services.models import *

from listener.models import * 
from listener.serializers import *

from app.events import main_location_machine

class IndividualTrackingView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei, customer_id):
		if imei:
			subscription = Subscription.objects.filter(imei_no=imei, device_listing=True, customer_id=customer_id).last()
			if subscription:
				check_if_exist = IndividualTracking.objects.filter(imei=imei).last()
				if check_if_exist:
					date_issued = datetime.datetime.strptime(check_if_exist.created_on.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
					current_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")

					diff = abs((current_time - date_issued).days)

					if diff>20:
						check_if_exist.delete()
						token = self.generate_token(imei)
						if token:
							return JsonResponse({'message':'New token for individiaul Tracking', 'status':True, 'status_code':200, 'token':token}, status=200)
						return JsonResponse({'message':'Error during generating token, please try again letter', 'status':True, 'status_code':500}, status=200)
					else:
						return JsonResponse({'message':'Old token not yet expired', 'status':True, 'status_code':200, 'token':check_if_exist.key}, status=200)
				else:
					token = self.generate_token(imei)
					if token:
						return JsonResponse({'message':'New token for individiaul Tracking', 'status':True, 'status_code':200, 'token':token}, status=200)
					return JsonResponse({'message':'Error during generating token, please try again letter', 'status':True, 'status_code':500}, status=200)
			return JsonResponse({'message':'Invalid parameters', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)


	def generate_token(self, imei):
		track_object = {}
		track_object['key'] = str(hashlib.sha1(imei.encode()).hexdigest())
		track_object['imei'] = imei

		serializer = IndividualTrackingSerializer(data=track_object)
		if serializer.is_valid():
			serializer.save()
			return track_object['key']
		else:
			return False


class ValidateTrackingTokenView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, token):
		check_if_exist = IndividualTracking.objects.filter(key=token).last()
		if check_if_exist:
			date_issued = datetime.datetime.strptime(check_if_exist.created_on.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
			current_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
			diff = abs((current_time - date_issued).days)
			if diff>20:
				check_if_exist.delete()
				return JsonResponse({'message':'Token Expired, please generate new token', 'status':False, 'status_code':400}, status=200)
			return JsonResponse({'message':'Valid Token', 'imei':check_if_exist.imei, 'status_code':200, 'status':True}, status=200)
		return JsonResponse({'message':'Invalid Token', 'status':False, 'status_code':400}, status=200)


class IndividualTrackDeviceDetails(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, token):
		try:
			category = request.GET['category']
		except(Exception)as e:
			return JsonResponse({'message':'Category required!', 'status':False, 'status_code':400}, status=200)

		check_if_exist = IndividualTracking.objects.filter(key=token).last()
		if check_if_exist:
			date_issued = datetime.datetime.strptime(check_if_exist.created_on.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
			current_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
			diff = abs((current_time - date_issued).days)
			if diff <= 20:
				device = Subscription.objects.filter(imei_no=check_if_exist.imei).last()
				if device:
					self.customer_id=device.customer_id
					serializer = DeviceListSerializer(device)
					if category == 'obd':
						details_to_send = self.get_device_details(serializer.data)
					elif category == 'gps':
						details_to_send = self.get_gl_device_details(serializer.data)
					return JsonResponse({'message':'Device Details successfully retrieved', 'status':True, 'status_code':200, 'device':details_to_send}, status=200)
			return JsonResponse({'message':'Token Expired', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Invalid Token', 'status':False, 'status_code':400}, status=200)


	def get_gl_device_details(self, device):
		fri_details = GLFriMarkers.objects.filter(imei=device.get('imei_no')).last()
		if fri_details:
			serializer = GLFriMarkersSerializer(fri_details)
			device['device_details'] = serializer.data
			device['vehicle_details'] = self.get_vehicle_details(device.get('imei_no'))
			device['meta_data'] = self.get_meta_data(self.customer_id)
		else:
			device['device_details'] = {}
		return device
		
	def get_device_details(self, device):
		# obd_details = ObdMarkers.objects.filter(imei=device['imei_no'], engine_rpm__isnull = False, vehicle_speed__isnull = False, engine_coolant_temp__isnull = False, fuel_consumption__isnull = False, throttle_position__isnull = False, engine_load__isnull = False, longitude__isnull=False, latitude__isnull=False).filter(~queue(fuel_consumption__in=['nan', 'null'])).last()
		obd_details = ObdMarkers.objects.filter(imei=device['imei_no'], longitude__isnull=False, latitude__isnull=False).last()
		if obd_details:
			serializer = DeviceObdMarkersSerializer(obd_details)
			device['device_details'] = serializer.data
			device['device_details']['device_status'] = self.get_device_status(device['imei_no'])
			device['vehicle_details'] = self.get_vehicle_details(device['imei_no'])
			device['meta_data'] = self.get_meta_data(self.customer_id)
		else:
			device['device_details'] = {}
		return device

	def get_device_status(self, imei):
		fri_details = FriMarkers.objects.filter(imei=imei, device_status__isnull=False).last()
		if fri_details:
			return fri_details.device_status
		return None

	def get_vehicle_details(self, imei):
		setting_instance = SettingsModel.objects.filter(imei=imei).last()
		if setting_instance:
			setting_obj={}
			setting_obj['vehicle_type'] = setting_instance.vehicle_type
			setting_obj['vehicle_color'] = setting_instance.vehicle_color
			return setting_obj
		return {}

	def get_meta_data(self, customer_id):
		user = User.objects.filter(customer_id=customer_id, subuser=False).last()
		if user:
			user_obj = {}
			user_obj['time_zone'] = user.time_zone
			user_obj['uom'] = user.uom
			return user_obj
		return {}


class IndividualTrackingLocation(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, lng, lat):
		token = request.GET.get('token', None)
		if token:
			validate = IndividualTracking.objects.filter(key=token).last()
			if validate:
				check_location = Location.objects.filter(longitude=lng, latitude=lat).first()
				# check_location = main_location_machine.get_location(lng, lat)
				if check_location:
					serializer = LocationSerializer(check_location)
					return JsonResponse({'message':'Retreiving location successfull', 'status_code':200, 'status':True, 'location':serializer.data}, status=200)
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
		# from app.events.main_location_machine import save_location
		# import _thread
		# _thread.start_new_thread(save_location, (location_obj,))
		# loop = asyncio.new_event_loop()
		# loop.run_in_executor(None, main_location_machine.save_location, [location_obj])

	def get_google_keys(self):
		google_key = GoogleMapAPIKey.objects.first()
		if google_key:
			return str(google_key.key)
		return str(settings.GOOGLE_MAP_KEY)