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

from app.serializers import *
from app.models import *


from listener.models import * 
from listener.serializers import *

from services.models import *

from .data import _data


exclude_obd = [None, 0, 0.0]
time_fmt = '%Y-%m-%d %H:%M:%S'



class CalculateBatteryApiView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		imei = request.GET.get('imei')
		date = request.GET.get('date', [])

		if date:
			date = date.split("-")
			if int(date[0])>31 or int(date[1])>12:
				return JsonResponse({'message':'Invalid Date format you are providing. Please Provide date as DD-MM-YYYY', 'status':False, 'status_code':400}, status=200)
		calculate = CalculateBatteryDrain()
		result = calculate.start(imei, date)
		return JsonResponse({'message':'Battery Drain Calculated', 'status':True, 'status_code':201}, status=201)


class CalculateBatteryDrain:
	def start(self, imei, date):
		timezone = self.get_time_zone(imei)

		if date:
			my_timestamp_in_new_timezone, to_my_timestamp_in_new_timezone = self.get_date_to_filter(timezone, date[0], date[1], date[2])
		else:
			local_datetime = datetime.datetime.now(pytz.timezone(timezone)) - timedelta(days=1)
			my_timestamp_in_new_timezone, to_my_timestamp_in_new_timezone = self.get_date_to_filter(timezone, local_datetime.day, local_datetime.month, local_datetime.year)
		
		records = self.get_data(imei, my_timestamp_in_new_timezone, to_my_timestamp_in_new_timezone)
		total_battery, total_time, total_mileage = self.start_calculating(records)

		if date:
			BatteryDrain.objects.filter(date__day=date[0], date__month=date[1], date__year=date[2], imei=imei).delete()
			serializer = BatteryDrainSerializer(data={
					"imei":imei,
					"mileage": '%.2f'%total_mileage,
					"time_spent":'%.2f'%total_time,
					"battery": '%.2f'%total_battery,
					"date" : datetime.datetime.strptime(str(date[0])+"-"+str(date[1])+"-"+str(date[2]), "%d-%m-%Y").date()
				})
			if serializer.is_valid():
				serializer.save()
			else:
				print(serializer.errors)
		else:
			BatteryDrain.objects.filter(date__day=local_datetime.day, date__month=local_datetime.month, date__year=local_datetime.year, imei=imei).delete()
			serializer = BatteryDrainSerializer(data={
					"imei":imei,
					"mileage": '%.2f'%total_mileage,
					"time_spent":'%.2f'%total_time,
					"battery": '%.2f'%total_battery,
					"date" : local_datetime.date()
				})
			if serializer.is_valid():
				serializer.save()
			else:
				print(serializer.errors)
		pass


	def start_calculating(self, data):
		calculated_data = []
		prev_battery = 0
		prev_mialege = 0

		mialege = 0
		start_mialege = 0
		end_mialege = 0

		start_battery = 0
		end_battery = 0

		start_sendtime = 0
		end_sendtime = 0

		calculated_record = []

		half_loop = 0

		imei = None

		for i in data:
			imei = i.get('imei')
			if not calculated_record:
				start_battery = i.get('battery_percentage')
				start_mialege = i.get('mileage')
				prev_battery = i.get('battery_percentage')
				prev_mialege = i.get('mileage')

				end_mialege = i.get('mileage')
				end_battery = i.get('battery_percentage')

				start_sendtime = i.get('send_time')
				end_sendtime = i.get('send_time')

				calculated_record.append(i)
				half_loop = half_loop + 1
			else:
				if float(prev_battery) < float(i.get('battery_percentage')):
					calculated_data.append(
						{
							"imei": imei,
							"start_battery": start_battery,
							"end_battery" : prev_battery,
							"start_mialege" : start_mialege,
							"end_mialege":end_mialege,
							"start_sendtime" : start_sendtime,
							"end_sendtime" : end_sendtime
						}
						)
						
					
					calculated_record = []
					start_battery = i.get('battery_percentage')
					start_mialege = i.get('mileage')

					prev_battery = i.get('battery_percentage')
					prev_mialege = i.get('mileage')

					end_mialege = i.get('mileage')
					end_battery = i.get('battery_percentage')

					start_sendtime = i.get('send_time')
					end_sendtime = i.get('send_time')

					calculated_record.append(i)
					half_loop = 1
				else:
					prev_battery = i.get('battery_percentage')
					prev_mialege = i.get('mileage')

					end_mialege = i.get('mileage')
					end_battery = i.get('battery_percentage')

					end_sendtime = i.get('send_time')
					
					calculated_record.append(i)

					half_loop = half_loop + 1


		if half_loop > 1:
			calculated_data.append(
				{
					"imei": imei,
					"start_battery": calculated_record[0].get('battery_percentage'),
					"end_battery" : calculated_record[-1].get('battery_percentage'),
					"start_mialege" : calculated_record[0].get('mileage'),
					"end_mialege":calculated_record[-1].get('mileage'),
					"start_sendtime" : calculated_record[0].get('send_time'),
					"end_sendtime" : calculated_record[-1].get('send_time')
				}
			)

		total_mileage = 0
		total_time = 0
		total_battery = 0

		for i in calculated_data:
			total_battery = (i.get('start_battery') - i.get('end_battery')) + total_battery
			total_time = (self.make_time_diff(str(i.get('start_sendtime')), str(i.get('end_sendtime')))) + total_time
			total_mileage = (i.get('end_mialege') - i.get('start_mialege')) + total_mileage

		return total_battery, total_time, total_mileage

	def make_time_diff(self, old_time, new_time):
		try:
			time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
				time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
			time_diff = time_diff/60
		except(Exception)as e:
			print(e)
			time_diff = 0
		return time_diff



	def get_data(self, imei, from_time_date, to_time_date):
		try:
			from_send_time = int(from_time_date.strftime("%Y%m%d%H%M%S"))
			to_send_time = int(to_time_date.strftime("%Y%m%d%H%M%S"))
			fri = GLFriMarkers.objects.filter(imei=imei, send_time__gte=from_send_time, send_time__lte=to_send_time).exclude(latitude = 0, longitude = 0, speed=0).all().order_by('send_time')
		except(Exception)as e:
			fri = GLFriMarkers.objects.filter(imei=imei, record_date__gte=from_time_date, record_date__lte=to_time_date).exclude(latitude = 0, longitude = 0, speed=0).all().order_by('send_time')

		fri_serializer = GLFriMarkersSerializer(fri, many=True).data
		
		data = list(fri_serializer)
		data = [dict(i) for i in data]

		data = [dict(t) for t in {tuple(d.items()) for d in data}]

		records = sorted(data, key = lambda i: i['send_time'])
		return records



	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			try:
				user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
				if user:
					return user.time_zone
			except(Exception)as e:
				print(e)
				return None
		return None


	def get_date_to_filter(self, timezone, day, month, year):
		old_timezone = pytz.timezone(timezone)
		new_timezone = pytz.timezone("UTC")

		timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', time_fmt)
		my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)

		to_timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', time_fmt)
		to_my_timestamp_in_new_timezone = old_timezone.localize(to_timestamp).astimezone(new_timezone)
		return my_timestamp_in_new_timezone, to_my_timestamp_in_new_timezone