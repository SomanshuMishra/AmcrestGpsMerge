from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import datetime

from .serializers import *
from .models import *


class ZoneAlertView(APIView):
	# permission_classes = (AllowAny,)
	def postold(self, request):
		error = []
		try:
			customer_id = request.user.customer_id
		except Exception as e:
			customer_id = None

		try:
			category = request.GET.get('category', 'gps')
		except(Exception)as e:
			return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)

		if str(customer_id) == str(request.data.get('customer_id')):
			if request.data.get('imei'):
				for imei in request.data.get('imei'):
					if request.data.get('zones', None):
						zone_error = self.create_zone_alert_for_device(imei, request.data, category)
						error.extend(zone_error)
					if request.data.get('zone_group', None):
						zone_group_error = self.create_zone_group_alert_for_device(imei, request.data, category)
						error.extend(zone_group_error)
				return JsonResponse({'message':'Zone Alert Created Successfully', 'errors':error, 'status_code':201, 'status':True}, status=201)
			return JsonResponse({'message':'Bad Request, Device IMEI Required', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Unauthorized Access', 'status':False, 'status_code':401}, status=401)
	
 
	def post(self, request):
		gps_error = []
		obd_error = []
		try:
			customer_id = request.user.customer_id
		except Exception as e:
			customer_id = None
		category1=  "category"
		category2=  "gps"
		if str(customer_id) == str(request.data.get('customer_id')):
			if request.data.get('imei'):
				for imei in request.data.get('imei'):
					if request.data.get('zones', None):
						# OBD Zone Error
						obd_zone_error = self.create_zone_alert_for_device(imei, request.data, category1)
						obd_error.extend(obd_zone_error)
						# GPS Zone Error
						gps_zone_error = self.create_zone_alert_for_device(imei, request.data, category2)
						gps_error.extend(obd_zone_error)
					if request.data.get('zone_group', None):
						# OBD Zone Group Error
						obd_zone_group_error = self.create_zone_group_alert_for_device(imei, request.data, category1)
						obd_error.extend(obd_zone_group_error)
						# GPS Zone Group Error
						gps_zone_group_error = self.create_zone_group_alert_for_device(imei, request.data, category2)
						gps_error.extend(gps_zone_group_error)
				return JsonResponse({'message':'Zone Alert Created Successfully', 'obd_errors':obd_error,'gps_errors':gps_error, 'status_code':201, 'status':True}, status=201)
			return JsonResponse({'message':'Bad Request, Device IMEI Required', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Unauthorized Access', 'status':False, 'status_code':401}, status=401)

	def create_zone_alert_for_device(self, imei, data, category):
		error = []
		for zone in data['zones']:
			data['zone'] = zone
			zone_instance = Zones.objects.filter(id=zone).first()
			if zone_instance:
				data['type'] = zone_instance.type
				data['imei'] = imei
				data['category'] = category
				serializer = ZoneAlertSerializer(data=data)
				if serializer.is_valid():
					serializer.save()
				else:
					zone_error_obj = {}
					zone_error_obj['zone'] = zone
					zone_error_obj['error'] = serializer.errors
					error.append(zone_error_obj)
			else:
				zone_error_obj = {}
				zone_error_obj['zone'] = zone
				zone_error_obj['error'] = {"zone_group":"Invalid Zone"}
				error.append(zone_error_obj)
		return error

	def create_zone_group_alert_for_device(self, imei, data, category):
		error = []
		data1 = data.copy()
		alert_name = data1.get('name', 'zone alert')
		zone_instances = Zones.objects.filter(zone_group=data1['zone_group']).all()
		for zone_instance in zone_instances:
			if zone_instance:
				 data1['zone'] = zone_instance.id
				 data1['type'] = zone_instance.type
				 data1['imei'] = imei
				 data1['name'] = alert_name+' ('+zone_instance.name+')'
				 data1['category'] = category
				 serializer = ZoneAlertSerializer(data=data1)
				 if serializer.is_valid():
				 	serializer.save()
				 else:
				 	zone_error_obj = {}
				 	zone_error_obj['zone_group'] = data1['zone_group']
				 	zone_error_obj['error'] = serializer.errors
				 	error.append(zone_error_obj)
			else:
				zone_error_obj = {}
				zone_error_obj['zone_group'] = data['zone_group']
				zone_error_obj['error'] = {"zone_group":"Invalid Zone Group"}
				error.append(zone_error_obj)
		return error


	def get(self, request):
		zone = request.GET.get('zone', None)
		customer_id_get = request.GET.get('customer_id', None)
		print(zone,customer_id_get)
		try:
			customer_id = request.user.customer_id
		except Exception as e:
			customer_id = None
		# try:
		# 	category = request.GET.get('category', None)
		# except(Exception)as e:
		# 	return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)
		category1 = 'gps'
		category2 = 'obd'
		print(customer_id,'cust')
		if customer_id_get:
			if str(customer_id) == str(customer_id_get):
				gps_zone_alert = ZoneAlert.objects.filter(customer_id=customer_id, category=category1).all()
				gps_serializer = ZoneAlertReadSerializer(gps_zone_alert, many=True)
				obd_zone_alert = ZoneAlert.objects.filter(customer_id=customer_id, category=category2).all()
				obd_serializer = ZoneAlertReadSerializer(obd_zone_alert, many=True)
				return JsonResponse({'message':'Zone Alert list of the user', 'status_code':200, 'status':True, 'gps_zone_alert':gps_serializer.data,'obd_zone_alert':obd_serializer.data}, status=200)
			return JsonResponse({'message':'Invalid Request, You are not Authorized to access', 'status_code':401, 'status':False}, status=401)
		elif zone:
			zone_instance = Zones.objects.filter(id=zone).first()
			if zone_instance:
				if str(zone_instance.customer_id) == str(customer_id):
					zone_alert = ZoneAlert.objects.filter(zone=zone).all()
					serializer = ZoneAlertReadSerializer(zone_alert, many=True)
					return JsonResponse({'message':'Zone Alert list by Zone', 'status_code':200, 'status':True, 'zone_alert':serializer.data}, status=200)
				return JsonResponse({'message':'Invalid Request, You are not Authorized to access', 'status_code':401, 'status':False}, status=401)
			return JsonResponse({'message':'Invalid Zone', 'status_code':404, 'status':False}, status=200)
		return JsonResponse({'message':'Bad Request, Zone ID or Customer ID Required', 'status':False, 'status_code':400}, status=200)


	def put(self, request):
		print(request.data)
		customer_id_get = request.data.get('customer_id', None)
		try:
			customer_id = request.user.customer_id
		except Exception as e:
			customer_id = None

		id = request.data.get('id', None)
		if id:
			if str(customer_id) == str(customer_id_get):
				zone_alert = ZoneAlert.objects.filter(customer_id=id).first()
				if zone_alert:
					if str(zone_alert.customer_id)== str(customer_id):
						serializer = ZoneAlertUpdateSerializer(zone_alert, data=request.data)
						if serializer.is_valid():
							serializer.save()
							return JsonResponse({'message':'Zone Alert updated Successfully', 'status_code':204, 'status':True}, status=200)
						return JsonResponse({'message':'Invalid Data', 'status_code':400, 'status':False, 'error':serializer.errors}, status=200)
					return JsonResponse({'message':'Unauthorized Access', 'status_code':401, 'status':False}, status=401)
				return JsonResponse({'message':'Invalid Zone, please select a valid zone', 'status':False, 'status_code':404}, status=200)
			return JsonResponse({'message':'Unauthorized Access', 'status_code':401, 'status':False}, status=401)
		return JsonResponse({'message':'Bad Request, ID Required', 'status':False, 'status_code':400}, status=200)


	def delete(self, request):
		try:
			customer_id = request.user.customer_id
		except Exception as e:
			customer_id = None

		id = request.data.get('id', None)
		if id:
			zone_alert = ZoneAlert.objects.filter(customer_id=id).first()
			if zone_alert:
				if str(zone_alert.customer_id)== str(customer_id):
					zone_alert.delete()
					return JsonResponse({'message':'Zone Alert Deleted Successfully', 'status':True, 'status_code':204}, status=200)
				return JsonResponse({'message':'Unauthorized Access', 'status_code':401, 'status':False}, status=401)
			return JsonResponse({'message':'Invalid Zone, please select a valid zone', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'Bad Request, ID Required', 'status':False, 'status_code':400}, status=200)


# class Zone