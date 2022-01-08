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

from listener.models import * 
from listener.serializers import *

from services.models import *
from services.device_frequency import *

class UpdateDeviceFrequency(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		imei = request.data.get('imei', None)
		device_frequency = request.data.get('device_frequency', None)

		sim_iccid = SimMapping.objects.filter(imei=imei).first()
		if not sim_iccid:
			return JsonResponse({'message':'Invalid IMEI, Device not found', 'status':False, 'status_code':404}, status=200)


		check_subscription = Subscription.objects.filter(imei_no=imei, sim_status=True).last()

		frequency = DeviceFrequency.objects.filter(device_frequency_key=device_frequency).first()
		frequency_obd = DeviceFrequencyObd.objects.filter(device_frequency_key=device_frequency).first()

		if frequency or frequency_obd:
			if check_subscription:
				setting_instance = SettingsModel.objects.filter(imei=imei).last()

				if device_frequency == '30_sec' or device_frequency == '30_sec_obd':
					# if check_subscription.activated_plan_id == '30_second_interval' or check_subscription.activated_plan_id == '30_second_interval_obd':
					if device_frequency:
						status = update_device_frequency(imei, device_frequency)
						if status:
							setting_instance.device_reporting_frequency = device_frequency
							setting_instance.device_reporting_frequency_desc = self.get_frequency_desc(device_frequency)
							setting_instance.trip_end_timer = self.calculate_trip_end_time(setting_instance.trip_end_timer, device_frequency)
							setting_instance.save()
							return JsonResponse({'message':'Device Frequency updated', 'status':True, 'status_code':200}, status=200)
						else:
							return JsonResponse({'message':'Error Durring, Updating Device Frequency', 'status':False, 'status_code':400}, status=200)
					else:
						return JsonResponse({'message':'Cannot upgrade device frequency to 30 Seconds, Please upgrade your subscription plan', 'status':True, 'status_code':200}, status=200)

				else:
					status = update_device_frequency(imei, device_frequency)

					if status:
						setting_instance.device_reporting_frequency = device_frequency
						setting_instance.device_reporting_frequency_desc = self.get_frequency_desc(device_frequency)
						setting_instance.trip_end_timer = self.calculate_trip_end_time(setting_instance.trip_end_timer, device_frequency)
						setting_instance.save()
						return JsonResponse({'message':'Updated Device Frequency successfully', 'status':True, 'status_code':200}, status=200)
					else:
						return JsonResponse({'message':'Error Durring, Updating Device Frequency', 'status':False, 'status_code':400}, status=200)
			return JsonResponse({'message':'Invalid IMEI, Device not found', 'status':False, 'status_code':404}, status=200)
		else:
			return JsonResponse({'message':'Invalid Device Frequency', 'status':False, 'status_code':400}, status=200)

	def get_frequency_desc(self, frequency_key):
		frequency = DeviceFrequency.objects.filter(device_frequency_key=frequency_key).first()
		frequency_obd = DeviceFrequencyObd.objects.filter(device_frequency_key=frequency_key).first()
		if frequency:
			return frequency.device_frequency_value
		elif frequency_obd:
			return frequency_obd.device_frequency_value
		return frequency_key


	def calculate_trip_end_time(self, end_timer, device_frequency):
		frequency = DeviceFrequency.objects.filter(device_frequency_key=device_frequency).first()
		if frequency:
			try:
				if end_timer < frequency.device_frequency:
					return end_timer
				else:
					return frequency.device_frequency*2
			except(Exception)as e:
				return 10
		return 10
