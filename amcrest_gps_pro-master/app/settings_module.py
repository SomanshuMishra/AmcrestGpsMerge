from django.shortcuts import render
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

from django.db import close_old_connections

import string
import random

from .serializers import *
from .models import *

from services.models import *
from services.serializers import *


class SettingModuleView(APIView):
	# permission_classes = (AllowAny,)
	def put(self, request, imei):
		self.imei = imei
		if request.data:
			if imei:
				self.category = category = request.GET.get('category', None)
				settings_module = SettingsModel.objects.filter(imei=imei).last()
				old_speed = settings_module.speed_limit
				self.speed = request.data.get('speed_limit', None)

				if category == 'gps':
					if settings_module:
						serializer = SettingsSerializer(settings_module, data=request.data)
						if serializer.is_valid():
							serializer.save()
							return JsonResponse({'message':'Settings Updated Successfully', 'status':True, 'status_code':204}, status=200)
						return JsonResponse({'message':'Invalid Settings', 'status':False, 'status_code':400, 'errors':serializer.errors}, status=200)
					return JsonResponse({'message':'Invalid Settings, device not found', 'status':False, 'status_code':404}, status=200)
				else:
					if settings_module:
						serializer = SettingsSerializer(settings_module, data=request.data)
						if serializer.is_valid():
							serializer.save()
							try:
								if self.speed:
									if old_speed != float(request.data.get('speed_limit', None)):
										subscription_instance = Subscription.objects.filter(imei_no=self.imei).last()
										if subscription_instance:
											if subscription_instance.device_model:
												if self.prepare_message(subscription_instance.device_model):
													if self.save_message():
														# self.update_speed()
														return JsonResponse({'message':'Settings Updated Successfully, Speed limit update Successfully', 'status':True, 'status_code':204}, status=200)
													self.send_error_mail()
													return JsonResponse({'message':'Settings Updated Successfully. Requested to update speed, changes will be done shortly.', 'status':True, 'status_code':204}, status=200)
												self.send_error_mail()
												return JsonResponse({'message':'Settings Updated Successfully. Requested to update speed, changes will be done shortly.', 'status':True, 'status_code':204}, status=200)
											self.send_error_mail()
											return JsonResponse({'message':'Settings Updated Successfully. Requested to update speed, changes will be done shortly.', 'status':True, 'status_code':204}, status=200)
										self.send_error_mail()
										return JsonResponse({'message':'Settings Updated Successfully. Requested to update speed, changes will be done shortly.', 'status':True, 'status_code':204}, status=200)
									return JsonResponse({'message':'Settings Updated Successfully', 'status':True, 'status_code':204}, status=200)
							except(Exception)as e:
								print(e)
								return JsonResponse({'message':'Settings Updated Successfully. Error during updating speed', 'status':True, 'status_code':204}, status=200)
							return JsonResponse({'message':'Settings Updated Successfully', 'status':True, 'status_code':204}, status=200)
						return JsonResponse({'message':'Invalid Settings', 'status':False, 'status_code':400, 'errors':serializer.errors}, status=200)
					return JsonResponse({'message':'Invalid Settings, device not found', 'status':False, 'status_code':404}, status=200)
			return JsonResponse({'message':'IMEI required to change settings of device', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)

	def get(self, request, imei):
		if imei:
			settings_instance = SettingsModel.objects.filter(imei=imei).last()
			if settings_instance:
				serializer = SettingsSerializer(settings_instance)
				return JsonResponse({'message':'Get Settings for the device success', 'status':True, 'status_code':200, 'settings':serializer.data}, status=200)
			return JsonResponse({'message':'Invalid IMEI, settings not found', 'status':False, 'status_code':404}, status=200)
		return JsonResponse({'message':'IMEI Required, Bad Request', 'status':False, 'status_code':400}, status=200)

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


class SettingDevicesView(APIView):
	# permission_classes = (AllowAny,)
	def getold(self, request, customer_id):
		try:
			category = request.GET['category']
		except(Exception)as e:
			return JsonResponse({'message':'Category required!', 'status':False, 'status_code':400}, status=200)

		category_list = self.get_device_categories(category)

		subscriptions = Subscription.objects.filter(customer_id=customer_id, device_model__in=category_list, device_in_use=True, device_listing=True).all()
		if subscriptions:
			imei = [subscription.imei_no for subscription in subscriptions]
			settings = SettingsModel.objects.filter(imei__in=imei).all()
			serializer = SettingsSerializer(settings, many=True)
			return JsonResponse({'message':'settings of device', 'status_code':200, 'status':True, 'settings':serializer.data}, status=200)
		else:
			return JsonResponse({'message':'Device not found', 'status_code':404, 'status':False, 'settings':[]}, status=200)

	def get(self, request, customer_id):
     
		gps_category_list = self.get_device_categories('gps')
		obd_category_list = self.get_device_categories('obd')
		
		gps_subscriptions = Subscription.objects.filter(customer_id=customer_id, device_model__in=gps_category_list, device_in_use=True, device_listing=True).all()
  
		obd_subscriptions = Subscription.objects.filter(customer_id=customer_id, device_model__in=obd_category_list, device_in_use=True, device_listing=True).all()
		if gps_subscriptions or obd_subscriptions:
			if gps_subscriptions:
				imei = [subscription.imei_no for subscription in gps_subscriptions]
				settings = SettingsModel.objects.filter(imei__in=imei).all()
				gps_serializer = SettingsSerializer(settings, many=True)
			if obd_subscriptions:
				imei = [subscription.imei_no for subscription in obd_subscriptions]
				settings = SettingsModel.objects.filter(imei__in=imei).all()
				obd_serializer = SettingsSerializer(settings, many=True)
			return JsonResponse({'message':'settings of device', 'status_code':200, 'status':True, 'gps_settings':gps_serializer.data,'obd_settings':obd_serializer.data}, status=200)
		else:
			return JsonResponse({'message':'Device not found', 'status_code':404, 'status':False, 'settings':[]}, status=200)


	def get_device_categories(self, category):
		categories = SimMapping.objects.filter(category=category).values('model').distinct()
		category_list = [i.get('model') for i in categories]
		return category_list