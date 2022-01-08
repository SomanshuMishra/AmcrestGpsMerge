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

from .location_finder import *
from .voltage import voltage_event_module

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
	"driver_score": "Driver Score",
    "record_date" : "Date"
}



class DriverScoreExportApiView(APIView):
    # permission_classes = (AllowAny, )
    def post(self, request):
        rows = request.data.get('data', None)
        unit = request.data.get('unit', 'KM')
        customer_id = request.data.get('customer_id', None)
        _type = request.data.get('type', 'csv')
        if customer_id:

            if _type == 'pdf':
                filename = 'driver_export_{}.pdf'.format(str(customer_id))
                encoded_string = ''
                font_config = FontConfiguration()
                html_string = render_to_string('driver_score_export.html',
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

                filename = 'driver_export_'+str(customer_id)+'.csv'
                data_frame.to_csv(filename, index=False)

            with open(filename, 'rb') as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                os.remove(filename)
            return JsonResponse({
                'message': 'Driver Score Exported',
                'status': True,
                'status_code': 200,
                'encoded_string': encoded_string.decode('utf-8'),
                }, status=200)
        return JsonResponse({'message': 'Customer ID required',
                                'status': False, 'status_code': 400},
                                status=200)


class DriverScoreView(APIView):
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
				voltage_instance = DriverScore.objects.filter(imei=imei, record_date__range=[filter_from_date, filter_to_date], customer_id=customer_id).all()
				serializer = DriverScoreSerializer(voltage_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Driver Score details', 'from_date':request_from_date, 'to_date':request_to_date, 'driver_score':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				voltage_instance = DriverScore.objects.filter(imei=imei, record_date__day=from_date[0], record_date__month=from_date[1], record_date__year=from_date[2], customer_id=customer_id).first()
				serializer = DriverScoreSerializer(voltage_instance)
				close_old_connections()
				return JsonResponse({'message':'Driver Score details', 'date':request_date, 'driver_score':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'voltage':[]}, status=200)








def driver_score_module(args):
	trip_id = args[0]
	fuel_event = DriverScoreMachine(trip_id)
	fuel_event.receive_trip_event()


class DriverScoreMachine:
	def __init__(self, trip_id):
		self.trip_id = trip_id
		self.imei = None
		self.fuel_consumption = []
		self.speed = []

	def receive_trip_event(self):
		try:
			trip = UserObdTrip.objects.filter(id=self.trip_id).first()
		except(Exception)as e:
			trip = None
		self.imei = trip.imei

		if trip and self.trip_id:
			try:
				trip_logs = trip.trip_log
			except(Exception)as e:
				trip_logs = None

			try:
				fuel_event = DriverScore.objects.filter(imei=self.imei, record_date=trip.record_date.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)
			
			for i in trip_logs:
				for j in i:

					try:
						instant_fuel_consumption = float(j.get('instant_fuel_consumption', 0))
					except(Exception)as e:
						instant_fuel_consumption = 0

					if instant_fuel_consumption>0:
						instant_fuel_consumption = instant_fuel_consumption/1000

					try:
						speed = float(j.get('speed', 0))
					except(Exception)as e:
						speed = 0

					self.fuel_consumption.append(instant_fuel_consumption)
					self.speed.append(speed)
		
		# print(sum(self.fuel_consumption))
		# print(sum(self.speed))
		

		try:
			fph = ((sum(self.fuel_consumption)/3600)/(sum(self.speed)/3600))*100
		except(Exception)as e:
			fph = 0

		# print(fph)
		try:
			score = (40+(1-(fph-6)/8)*60)
		except(Exception)as e:
			print(e)
			score = 0


		customer_id = self.get_customer_id(self.imei)
		voltage_obj = {
			'imei': self.imei,
			'driver_score': score,
			'record_date':trip.record_date.date(),
			'customer_id':customer_id
		}
		serializer = DriverScoreSerializer(data=voltage_obj)
		if serializer.is_valid():
			serializer.save()
			print('-------------saved')
			close_old_connections()


		# fph = self.fuel_consumption

			# start_trip_log = trip_logs[0]
			# end_trip_log = trip_logs[-1]

			# if start_trip_log[0].get('fuel_consumption'):
			# 	start_fuel = start_trip_log[0].get('fuel_consumption')
			# else:
			# 	start_fuel = start_trip_log[1].get('fuel_consumption')


			# if end_trip_log[-1].get('fuel_consumption'):
			# 	end_fuel = end_trip_log[-1].get('fuel_consumption')
			# else:
			# 	end_fuel = end_trip_log[-2].get('fuel_consumption')


			# if start_trip_log[0].get('mileage'):
			# 	start_mileage = start_trip_log[0].get('mileage')
			# else:
			# 	start_mileage = start_trip_log[1].get('mileage')


			# if end_trip_log[-1].get('mileage'):
			# 	end_mileage = end_trip_log[-1].get('mileage')
			# else:
			# 	end_mileage = end_trip_log[-2].get('mileage')

			# try:
			# 	fuel_consumed = float(end_fuel) - float(start_fuel)
			# except(Exception)as e:
			# 	fuel_consumed = 0


			# try:
			# 	mileage = float(end_mileage) - float(start_mileage)
			# except(Exception)as e:
			# 	mileage = 0

			# try:
			# 	economy = (mileage/fuel_consumed)*100
			# except(Exception)as e:
			# 	economy = 0


			# customer_id = self.get_customer_id(self.imei)
			# voltage_obj = {
			# 	'imei': self.imei,
			# 	'fuel_economy': economy,
			# 	'record_date':trip.record_date.date(),
			# 	'customer_id':customer_id
			# }
			# serializer = DriverScoreSerializer(data=voltage_obj)
			# if serializer.is_valid():
			# 	serializer.save()
			# 	print('-------------saved')
			# 	close_old_connections()


	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None





			# for trip_log in trip_logs:

			# 	start_trip_time = self.format_date(trip_log[0].get('send_time'))
			# 	end_trip_time = self.format_date(trip_log[-1].get('send_time'))
				
			# 	try:
			# 		# self.prepare_trip_event(self.imei, trip_log[0], trip_log[-1], start_trip_time, end_trip_time, trip.record_date)
			# 		_thread.start_new_thread(prepare_trip_event, (self.imei, trip_log[0], trip_log[-1], start_trip_time, end_trip_time, trip.record_date_timezone))
			# 	except(Exception)as e:
			# 		print(e)
			# 		pass
			# 	close_old_connections()
			# 	# time.sleep(1)

			# _thread.start_new_thread(voltage_event_module, (self.imei, self.trip_id, trip.record_date_timezone.date(), trip.record_date.date()))


	def format_date(self, date):
		date_time = datetime.datetime.strptime(date[:4]+'-'+date[4:6]+'-'+date[6:8]+' '+date[-6:-4]+':'+date[-4:-2]+':'+date[-2:], date_time_fmt)
		time_zone = self.get_time_zone(self.imei)
		date_time = date_time.astimezone(pytz.timezone(time_zone))
		return date_time

	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
			close_old_connections()
			if user:
				return user.time_zone
		close_old_connections()
		return 'UTC'

	def prepare_trip_event(self, imei, start_trip_obj, end_trip_obj, start_time, end_time, trip_date):
		start_location = 'Unknown'
		end_location = 'Unknown'
		# try:
		# 	start_location = get_location(start_trip_obj.get('longitude', None), start_trip_obj.get('latitude', None))
		# 	end_location = get_location(end_trip_obj.get('longitude', None), end_trip_obj.get('latitude', None))
		# except(Exception)as e:
		# 	start_location = 'Unknown'
		# 	end_location = 'Unknown'

		customer_id = self.get_customer_id(imei)

		trip_start_obj = {
			'imei':imei,
			'type': 'start_trip',
			'location' : start_location,
			'date' : start_time.date(),
			'time' : start_time.time(),
			'record_date' :trip_date.date(),
			'customer_id' : customer_id
		} 

		self.save_trip_events(trip_start_obj)

		trip_end_obj = {
			'imei':imei,
			'type': 'end_trip',
			'location' : end_location,
			'date' : end_time.date(),
			'time' : end_time.time(),
			'record_date' :trip_date.date(),
			'customer_id' : customer_id
		}
		self.save_trip_events(trip_end_obj)


	def save_trip_events(self, event):
		serializer = TripEventsSerializer(data=event)
		if serializer.is_valid():
			serializer.save()

		else:
			print(serializer.errors)
		close_old_connections()

	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None