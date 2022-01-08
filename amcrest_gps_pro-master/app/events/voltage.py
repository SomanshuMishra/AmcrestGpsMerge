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


from app.serializers import *
from app.models import *

from .location_finder import *

from django.contrib.auth import get_user_model
User = get_user_model()

time_fmt = '%H:%M:%S'
date_fmt = '%Y-%m-%d'
date_time_fmt = '%Y-%m-%d %H:%M:%S'


import os
import base64
import pandas as pd

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.template import Context
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


trip_columns = {
    "imei" : "IMEI",
    "min_voltage": "Min Voltage (V)",
	"max_voltage": "Max Voltage (V)",
	"avg_voltage": "Avg Voltage (V)",
    "record_date" : "Date"
}



class VoltageExportApiView(APIView):
    # permission_classes = (AllowAny, )
    def post(self, request):
        rows = request.data.get('data', None)
        unit = request.data.get('unit', 'KM')
        customer_id = request.data.get('customer_id', None)
        _type = request.data.get('type', 'csv')
        if customer_id:
            # if rows:
            #     new_rows = []
            #     count = 1
            #     for i in rows:
            #         i['count'] = count
            #         count = count + 1
            #         new_rows.append(i)
            #     rows = new_rows

            if _type == 'pdf':
                filename = 'voltage_export_{}.pdf'.format(str(customer_id))
                encoded_string = ''
                font_config = FontConfiguration()
                html_string = render_to_string('voltage_export.html',
                        {'data': rows})
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

                html.write_pdf(target=filename, stylesheets=[css],
                               font_config=font_config)
            else:
                data_frame = pd.DataFrame(rows)
                data_frame = data_frame.rename(index=str, columns=trip_columns)

                filename = 'voltage_export_'+str(customer_id)+'.csv'
                data_frame.to_csv(filename, index=False)

            with open(filename, 'rb') as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                os.remove(filename)
            return JsonResponse({
                'message': 'Voltage Exported',
                'status': True,
                'status_code': 200,
                'encoded_string': encoded_string.decode('utf-8'),
                }, status=200)
        return JsonResponse({'message': 'Customer ID required',
                                'status': False, 'status_code': 400},
                                status=200)


class VoltageView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei):
		request_from_date = request.GET.get('from', None)
		request_to_date = request.GET.get('to', None)
		request_date = request.GET.get('date', None)

		if request_from_date and request_to_date:
			try:
				from_date = request_from_date.split('-')
				to_date = request_to_date.split('-')

				filter_from_date = from_date[2]+"-"+from_date[1]+"-"+from_date[0]
				filter_to_date = to_date[2]+"-"+to_date[1]+"-"+to_date[0]
				voltage_instance = VoltageModel.objects.filter(imei=imei, record_date__range=[filter_from_date, filter_to_date], customer_id=customer_id).all()
				serializer = VoltageSerializer(voltage_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Voltage details', 'from_date':request_from_date, 'to_date':request_to_date, 'voltage':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				voltage_instance = VoltageModel.objects.filter(imei=imei, record_date__day=from_date[0], record_date__month=from_date[1], record_date__year=from_date[2], customer_id=customer_id).first()
				serializer = VoltageSerializer(voltage_instance)
				close_old_connections()
				return JsonResponse({'message':'voltage details', 'date':request_date, 'voltage':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'voltage':[]}, status=200)









def voltage_event_module(args):
	trip_id = args[0]
	imei = args[1]
	trip = UserObdTrip.objects.filter(id=trip_id).first()
	if trip and trip_id:
		try:
			trip_logs = trip.trip_log
		except(Exception)as e:
			print(e)
			trip_logs = None

		# _thread.start_new_thread(voltage_event_module, (imei, trip_id, trip.record_date_timezone.date(), trip.record_date.date()))
		try:
			voltage_event = VoltageEventsMachine(imei, trip_id, trip.record_date_timezone.date(), trip.record_date.date())
			voltage_event.receive_trip_event()
		except(Exception)as e:
			print(e)

# def voltage_event_module(trip_id, imei, date, utc_date):
# 	print('voltage transfer')
# 	voltage_event = VoltageEventsMachine(trip_id, imei, date, utc_date)
# 	voltage_event.receive_trip_event()



class VoltageEventsMachine:
	def __init__(self, imei, trip_id, date, utc_date):
		self.imei = imei
		self.trip_id = trip_id
		self.date = date
		self.utc_date = utc_date


	def receive_trip_event(self):
		trip = UserObdTrip.objects.filter(id=self.trip_id).first()
		if trip:
			max_voltage, min_voltage, avg_voltage = self.get_max_min_voltage(trip.trip_log)
			self.check_and_update_voltage(self.imei, max_voltage, min_voltage, avg_voltage, self.date, self.utc_date)


	def get_max_min_voltage(self, trip_log):
		voltage_list = []
		max_vol = None
		min_vol = None
		avg_vol = None
		try:
			vol = [[ float(trip_item.get('obd_power_voltage')) for trip_item in trip if trip_item.get('obd_power_voltage') and trip_item.get('obd_power_voltage') != None and trip_item.get('obd_power_voltage') != 'nan' ] for trip in trip_log if trip]
		except(Exception)as e:
			print(e)
			vol = None


		if not vol:
			try:
				for trip in trip_log:
					for trip_item in trip:
						if trip_item.get('obd_power_voltage') and trip_item.get('obd_power_voltage') != None and trip_item.get('obd_power_voltage') != 'nan':
							voltage_list.append(float(trip_item.get('obd_power_voltage')))
			except(Exception)as e:
				print(e)
				pass

			max_vol = max(voltage_list)
			min_vol = min(voltage_list)
			avg_vol = sum(voltage_list)/len(voltage_list)
		else:
			try:
				max_vol = max(vol[0])
			except(Exception)as e:
				max_vol = 0

			try:
				min_vol = min(vol[0])
			except(Exception)as e:
				min_vol = 0

			try:
				avg_vol = sum(vol[0])/len(vol[0])
			except(Exception)as e:
				avg_vol = 0

			
			
		return max_vol, min_vol, avg_vol


	def check_and_update_voltage(self, imei, max_vol, min_vol, avg_vol, date, utc_date):
		
		voltage_instance = VoltageModel.objects.filter(imei=imei, record_date=date).last()
		if voltage_instance:
			if voltage_instance.min_voltage:
				if voltage_instance.min_voltage > min_vol:
					voltage_instance.min_voltage = min_vol
				else:
					voltage_instance.min_voltage = voltage_instance.min_voltage
			else:
				voltage_instance.min_voltage = min_vol

			if voltage_instance.max_voltage:
				if voltage_instance.max_voltage < max_vol:
					voltage_instance.max_voltage = max_vol
				else:
					voltage_instance.max_voltage = voltage_instance.max_voltage
			else:
				voltage_instance.max_voltage = max_vol

			
			voltage_instance.avg_voltage = round(avg_vol, 2)
			voltage_instance.save()
			# close_old_connections()
		else:
			customer_id = self.get_customer_id(imei)
			voltage_obj = {
				'imei': imei,
				'min_voltage': min_vol,
				'max_voltage':max_vol,
				'avg_voltage':round(avg_vol, 2),
				'record_date':date,
				'customer_id':customer_id
			}
			serializer = VoltageSerializer(data=voltage_obj)
			if serializer.is_valid():
				serializer.save()
				# close_old_connections()
			else:
				print(serializer.errors)


	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		# close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None