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


from listener.models import * 
from listener.serializers import *


class TelemetryObdDataView(APIView):
	# permission_classes = (AllowAny,)

	def __init__(self):
		self.main_list = []

	def get(self, request, imei):
		request_from_date = request.GET.get('from', None)
		request_to_date = request.GET.get('to', None)
		request_date = request.GET.get('date', None)
		main_list_to_send = []

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')

			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")

			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
			self.get_attach_dettach_data(record_date_gte, record_date_lte, imei)
			self.get_battery_low_data(record_date_gte, record_date_lte, imei)
			self.get_crash_report_data(record_date_gte, record_date_lte, imei)
			self.get_engine_summary_data(record_date_gte, record_date_lte, imei)
			self.get_harsh_behaviour_data(record_date_gte, record_date_lte, imei)
			self.get_ignition_data(record_date_gte, record_date_lte, imei)
			self.get_obd_data(record_date_gte, record_date_lte, imei)
			# main_list_to_send = sorted(self.main_list, key = lambda i: i.get('send_time', None))
			main_list_to_send = sorted(self.main_list, key = lambda i: i.get('send_time', None), reverse=False)
		return JsonResponse({'message':'Telemetry data', 'status':True, 'status_code':200, 'telimetry_data':main_list_to_send}, status=200)



	def get_attach_dettach_data(self, from_date, to_date, imei):
		attach_dettach = AttachDettach.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if attach_dettach:
			serializer = AttachDettachTelimetry(attach_dettach, many=True)
			self.main_list.extend(serializer.data)
		pass


	def get_battery_low_data(self, from_date, to_date, imei):
		battery_low = BatteryLow.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if battery_low:
			serializer = BatteryLowTelimetry(battery_low, many=True)
			self.main_list.extend(serializer.data)
		pass


	def get_crash_report_data(self, from_date, to_date, imei):
		crash_report = CrashReport.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if crash_report:
			serializer = CrashReportTelimetry(crash_report, many=True)
			self.main_list.extend(serializer.data)
		pass

	def get_engine_summary_data(self, from_date, to_date, imei):
		engine_summary = EngineSummary.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if engine_summary:
			serializer = EngineSummaryTelimetry(engine_summary, many=True)
			self.main_list.extend(serializer.data)
		pass


	def get_fri_markers_data(self, from_date, to_date, imei):
		fri_markers = FriMarkers.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if fri_markers:
			serializer = FriMarkersTelimetry(fri_markers, many=True)
			self.main_list.extend(serializer.data)
		pass


	def get_harsh_behaviour_data(self, from_date, to_date, imei):
		harsh = HarshBehaviour.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if harsh:
			serializer = HarshBehaviourTelimetry(harsh, many=True)
			self.main_list.extend(serializer.data)
		pass

	def get_ignition_data(self, from_date, to_date, imei):
		ignition = IgnitionOnoff.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if ignition:
			serializer = IgnitionOnoffTelimetry(ignition, many=True)
			self.main_list.extend(serializer.data)
		pass

	def get_obd_data(self, from_date, to_date, imei):
		obd = ObdMarkers.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		if obd:
			serializer = ObdMarkersTelimetry(obd, many=True)
			self.main_list.extend(serializer.data)
		pass

import pandas as pd
TELEMETRY = ["send_time", "report_name", "state", "imei", "latitude", "longitude", "speed", "mileage", "battery_percentage",  "azimuth","altitude", "mcc", "mnc","lac"]
TELEMETRY_RENAME = {
	"send_time":"Date Time (Customer Timezone)", 
	"report_name":"Report Name", 
	"imei": "IMEI", 
	"latitude": "Latitude", 
	"longitude":"Longitude", 
	"speed": "Speed", 
	"mileage":"Odometer", 
	"battery_percentage":"Battery Percentage", 
	"state": "State", 
	"azimuth":"Azimuth",
	"altitude":"Altitude", 
	"mcc":"MCC", 
	"mnc": "MNC",
	"lac": "LAC"
}

class TelemetryGlDataView(APIView):
	# permission_classes = (AllowAny,)

	def __init__(self):
		self.main_list = []

	def get(self, request, imei):
		request_from_date = request.GET.get('from', None)
		request_to_date = request.GET.get('to', None)
		request_date = request.GET.get('date', None)
		main_list_to_send = []
		data_frame_to_send = []

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')

			try:
				# record_date_send_time = 
				if len(from_date[1]) == 2:
					pass
				else:
					from_date[1] = '0'+from_date[1]


				if len(from_date[0]) == 2:
					pass
				else:
					from_date[0] = '0'+from_date[0]

				if len(to_date[1]) == 2:
					pass
				else:
					to_date[1] = '0'+to_date[1]


				if len(to_date[0]) == 2:
					pass
				else:
					to_date[0] = '0'+to_date[0]

				record_date_gte = from_date[2]+""+from_date[1]+""+from_date[0]+"000000"
				record_date_lte = to_date[2]+""+to_date[1]+""+to_date[0]+"235959"

				# record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				# record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")

			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
			
			
			self.get_stt_markers_data(record_date_gte, record_date_lte, imei)
			self.get_battery_model_data(record_date_gte, record_date_lte, imei)
			self.get_power_data(record_date_gte, record_date_lte, imei)
			self.get_sos_data(record_date_gte, record_date_lte, imei)
			self.get_gl_fri_data(record_date_gte, record_date_lte, imei)
			# main_list_to_send = sorted(self.main_list, key = lambda i: i.get('send_time', 0))
			# print(self.main_list)
			main_list_to_send = sorted(self.main_list, key = lambda i: i.get('send_time', None))
			data_frame = pd.DataFrame(main_list_to_send, columns=TELEMETRY)
			data_frame = data_frame.rename(index=str, columns=TELEMETRY_RENAME)
			data_frame_to_send = data_frame.to_json(orient='records')
		return JsonResponse({'message':'Telemetry data', 'status':True, 'status_code':200, 'telimetry_data':data_frame_to_send}, status=200)



	def get_stt_markers_data(self, from_date, to_date, imei):
		# attach_dettach = SttMarkers.objects.filter(record_date__gte=from_date, record_date__lte=to_date, imei=imei).order_by('record_date')
		attach_dettach = SttMarkersBackup.objects.filter(send_time__gte=from_date, send_time__lte=to_date, imei=imei).order_by('send_time')
		print(attach_dettach, 'fffffffffffffff')
		if attach_dettach:
			serializer = SttMarkersBackupTelimetry(attach_dettach, many=True)
			self.main_list.extend(serializer.data)
		pass


	def get_battery_model_data(self, from_date, to_date, imei):
		battery_low = BatteryModel.objects.filter(send_time__gte=from_date, send_time__lte=to_date, imei=imei).order_by('send_time')
		if battery_low:
			serializer = BatteryModelTelimetry(battery_low, many=True)
			self.main_list.extend(serializer.data)
		pass


	def get_power_data(self, from_date, to_date, imei):
		power = Power.objects.filter(send_time__gte=from_date, send_time__lte=to_date, imei=imei).order_by('send_time')
		if power:
			serializer = PowerTelimetry(power, many=True)
			self.main_list.extend(serializer.data)
		pass

	def get_sos_data(self, from_date, to_date, imei):
		engine_summary = SOS.objects.filter(send_time__gte=from_date, send_time__lte=to_date, imei=imei).order_by('send_time')
		if engine_summary:
			serializer = SOSTelimetry(engine_summary, many=True)
			self.main_list.extend(serializer.data)
		pass


	def get_gl_fri_data(self, from_date, to_date, imei):
		fri_markers = GLFriMarkersBackup.objects.filter(send_time__gte=from_date, send_time__lte=to_date, imei=imei).order_by('send_time')
		if fri_markers:
			serializer = GLFriMarkersBackupTelimetry(fri_markers, many=True)
			self.main_list.extend(serializer.data)
		pass


	





