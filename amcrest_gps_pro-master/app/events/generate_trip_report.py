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
from django.db.models import Q
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import json
import datetime
import time
import pytz
import _thread



from app.serializers import *
from app.models import *

from app.trip_notification.trip_location_finder import *

from django.contrib.auth import get_user_model
User = get_user_model()

time_fmt = '%H:%M:%S'
date_fmt = '%Y-%m-%d'
date_time_fmt = '%Y-%m-%d %H:%M:%S'



class GenerateTripReport(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.device_name = ''
		self.timezone_tz = 'UTC'

	def post(self, request):
		imei = request.data.get('imei', None)
		date = request.data.get('date', None)

		date = date.split('-')
		report = []

		if imei and date:
			self.timezone_tz = self.get_time_zone(imei)
			record_date_gte = datetime.datetime.strptime(date[2]+"-"+date[1]+"-"+date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
			record_date_lte = datetime.datetime.strptime(date[2]+"-"+date[1]+"-"+date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
			user_trip = UserTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).first()
			serializer = UserTripSerializer(user_trip)

			for i in serializer.data['trip_log']:
				start_re, end_re = self.generate_report(i, imei)
				report.append(start_re)
				report.append(end_re)
			return JsonResponse({'message':'Trip Report', 'status':True, 'status_code':200, 'report':report}, status=200)
		return JsonResponse({'message':'IMEI and Date required', 'status':False, 'status_code':400}, status=200)


	def generate_report(self, data, imei):
		start_report_to_send = {
			"imei" : imei,
			"alert_name" : "Trip Started",
			"device_name" : self.device_name,
			"event_type" : "trip_started",
			"location" : get_location(data[0].get('longitude'), data[0].get('latitude')),
			"longitude" : data[0].get('longitude'),
			"latitude" : data[0].get('latitude'),
			"type" : "alert",
			"event" : "started",
			"speed" : data[0].get('speed'),
			"record_date_timezone": self.prepare_time(data[0].get('send_time'))
		}

		end_report_to_send = {
			"imei" : imei,
			"alert_name" : "Trip Ended",
			"device_name" : self.device_name,
			"event_type" : "trip_ended",
			"location" : get_location(data[-1].get('longitude'), data[-1].get('latitude')),
			"longitude" : data[-1].get('longitude'),
			"latitude" : data[-1].get('latitude'),
			"type" : "alert",
			"event" : "started",
			"speed" : data[-1].get('speed'),
			"record_date_timezone": self.prepare_time(data[-1].get('send_time'))
		}

		return start_report_to_send, end_report_to_send

	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			self.device_name = str(sub.device_name)
			user = User.objects.filter(customer_id=sub.customer_id, subuser=False).last()
			if user:
				return user.time_zone
		return 'UTC'

	def prepare_time(self, time_value):
		timestamp = datetime.datetime.strptime(str(time_value[:4])+'-'+str(time_value[4:6])+'-'+str(time_value[6:8])+' '+time_value[-6:-4]+':'+time_value[-4:-2]+':'+time_value[-2:], date_time_fmt)
		new_timezone = pytz.timezone(self.timezone_tz)
		old_timezone = pytz.timezone("UTC")
		my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
		return datetime.datetime.strftime(my_timestamp_in_new_timezone, date_time_fmt)



trip_columns = {
    "device_name":"Device Name",
    "imei" : "IMEI",
    "alert_name" : "Event",
    "location" : "Location",
    "record_date_timezone" : "Date & Time"
}

import asyncio
import hashlib
import os
import base64
import pandas as pd
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.template import Context
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class ExportTripReport(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		customer_id = request.data.get('customer_id', None)
		rows = request.data.get('data', None)
		_type = request.data.get('type', 'csv') 
		if customer_id and rows:
			if _type == 'pdf':
				filename = 'trip_report_export_{}.pdf'.format(str(customer_id))
				encoded_string = ''
				font_config = FontConfiguration()
				html_string = render_to_string('trip_report_export.html', {'data': rows})
				html = HTML(string=html_string)
				css = \
					CSS(string='''
						@page { size: A4; margin: 1cm }
						@font-face {
							font-family: Gentium;
							src: url(http://example.com/fonts/Gentium.otf);
							}
							h1 { font-family: Gentium }
							img{
							height:20px;
							}''',
						font_config=font_config)
				html.write_pdf(target=filename, stylesheets=[css], font_config=font_config)
			else:
				rows = [{"device_name" : i.get('device_name', ''),
						"imei" : i.get('imei', ''),
						"alert_name" : i.get('alert_name', ''),
						"location" : i.get('location', ''),
						"record_date_timezone" : i.get('record_date_timezone', '')} for i in rows]
				data_frame = pd.DataFrame(rows)
				data_frame = data_frame.rename(index=str, columns=trip_columns)
				filename = 'trip_report_export'+str(customer_id)+'.csv'
				data_frame.to_csv(filename, index=False)

			with open(filename, 'rb') as pdf_file:
				encoded_string = base64.b64encode(pdf_file.read())
				os.remove(filename)
			return JsonResponse({
				'message': 'Trip Report Exported',
				'status': True,
				'status_code': 200,
				'encoded_string': encoded_string.decode('utf-8'),
				}, status=200)
		return JsonResponse({'message': 'Customer ID required', 'status': False, 'status_code': 400},status=200)