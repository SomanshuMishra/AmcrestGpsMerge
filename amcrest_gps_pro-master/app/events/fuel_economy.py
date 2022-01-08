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

from listener.models import *
from listener.serializers import *

from .location_finder import *
from .voltage import voltage_event_module

from django.contrib.auth import get_user_model
User = get_user_model()

time_fmt = '%H:%M:%S'
date_fmt = '%Y-%m-%d'
date_time_fmt = '%Y-%m-%d %H:%M:%S'



class FuelEconomyView(APIView):
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
				voltage_instance = FuelEconomy.objects.filter(imei=imei, record_date__range=[filter_from_date, filter_to_date], customer_id=customer_id, fuel_economy__isnull=False).all()
				
				serializer = FuelEconomySerializer(voltage_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Fuel Economy details', 'from_date':request_from_date, 'to_date':request_to_date, 'voltage':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				voltage_instance = FuelEconomy.objects.filter(imei=imei, record_date__day=from_date[0], record_date__month=from_date[1], record_date__year=from_date[2], customer_id=customer_id, fuel_economy__isnull=False).first()
				serializer = FuelEconomySerializer(voltage_instance)
				close_old_connections()
				return JsonResponse({'message':'Fuel Economy details', 'date':request_date, 'voltage':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'voltage':[]}, status=200)




# def fuel_economy_module_new(imei, details):
# 	fuel_economy = FuelEconomyNewModule(imei)
# 	fuel_economy.calculate()


# class FuelEconomyNewModule:
# 	def __init__(self, imei):
# 		self.imei = imei
# 		self.fuel_capacity = self.get_fuel_capacity(imei)
# 		self.fuel_capacity_per = None
# 		self.fuel_economy_per_km = None
# 		self.customer_id = None

# 	def calculate(self):
# 		timezone = self.get_time_zone(self.imei)
# 		if timezone:
# 			time.sleep(0.2)
# 			fuel_economy_list = []
# 			fuel_emission_list = []
# 			local_datetime = datetime.datetime.now(pytz.timezone(timezone))
# 			time_to_start, time_to_end = self.get_date_to_filter(timezone, local_datetime.day, local_datetime.month, local_datetime.year)
# 			data = self.get_data(self.imei, time_to_start, time_to_end)

# 			# print(data)
# 			if self.fuel_capacity:
# 				for d in data:
# 					if d.get('journey_fuel_consumption') and d.get('trip_mileage'):
# 						fuel_capacity_per = (float(d.get('journey_fuel_consumption'))/100)*self.fuel_capacity
# 						fuel_economy_per_km = 1/fuel_capacity_per
# 						fuel_economy_list.append(d.get('trip_mileage')*fuel_economy_per_km)
# 						fuel_emission_list.append(fuel_capacity_per)
# 			if fuel_economy_list:
# 				final_fuel_economy = sum(fuel_economy_list)/len(fuel_economy_list)
# 				self.save_fuel_economy(self.imei, local_datetime.date(), final_fuel_economy)

# 			if fuel_emission_list:
# 				self.save_fuel_emission(self.imei, time_to_start.date(), fuel_emission_list)
# 		pass


	# def save_fuel_economy(self, imei, date, fuel_economy):
	# 	if fuel_economy:
	# 		fuel_event = FuelEconomy.objects.filter(imei=imei, record_date=date).all()
	# 		if fuel_event:
	# 			fuel_event.delete()
	# 		voltage_obj = {
	# 			'imei': imei,
	# 			'fuel_economy': fuel_economy,
	# 			'record_date':date,
	# 			'customer_id':self.customer_id
	# 		}
	# 		serializer = FuelEconomySerializer(data=voltage_obj)
	# 		if serializer.is_valid():
	# 			serializer.save()
	# 			close_old_connections()
	# 	pass

# 	def save_fuel_emission(self, imei, date, emission):
# 		if emission:
# 			emission_obj = Emission.objects.filter(imei=imei, record_date=date).all()
# 			if emission_obj:
# 				emission_obj.delete()

# 			economy = sum(emission)*8.8
# 			voltage_obj = {
# 				'imei': imei,
# 				'emission': economy,
# 				'record_date':date,
# 				'customer_id':self.customer_id
# 			}
# 			serializer = EmissionSerializer(data=voltage_obj)
# 			if serializer.is_valid():
# 				serializer.save()
# 				close_old_connections()
# 		pass


# 	def get_data(self, imei, time_date_start, time_date_end):
# 		try:
# 			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
# 			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
# 			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()
# 		except(Exception)as e:
# 			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
# 			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
# 			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()

# 		stt_serializer = EngineSummarySerializer(stt, many=True).data
# 		data = [dict(i) for i in stt_serializer]
# 		records = sorted(data, key = lambda i: i['send_time'],reverse=False)
# 		return records

# 	def get_time_zone(self, imei):
# 		sub = Subscription.objects.filter(imei_no=imei).last()
# 		if sub:
# 			self.customer_id = sub.customer_id
# 			try:
# 				user = User.objects.filter(customer_id=sub.customer_id).first()
# 				if user:
# 					return user.time_zone
# 			except(Exception)as e:
# 				print(e)
# 				return None
# 		return None


# 	def get_fuel_capacity(self, imei):
# 		fuel = SettingsModel.objects.filter(imei=imei).last()
# 		if fuel:
# 			if fuel.fuel_capacity:
# 				return fuel.fuel_capacity
# 			return None
# 		return None


# 	def get_date_to_filter(self, timezone, day, month, year):
# 		timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', date_time_fmt)
# 		old_timezone = pytz.timezone(timezone)

# 		new_timezone = pytz.timezone("UTC")
# 		my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
# 		timestamp_end = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', date_time_fmt)
# 		old_timezone_end = pytz.timezone(timezone)
# 		new_timezone_end = pytz.timezone("UTC")
# 		my_timestamp_in_new_timezone_end = old_timezone_end.localize(timestamp_end).astimezone(new_timezone_end)
# 		return my_timestamp_in_new_timezone, my_timestamp_in_new_timezone_end



class ManualGenerateFuelEconomy(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.imei = None
		self.day = None
		self.month = None
		self.year = None

	def post(self, request):
		self.imei = request.data.get('imei', None)
		date = request.data.get('date', None)
		dates = date.split('-')
		if self.imei and date:
			fuel_economy = FuelEconomyManualGenerate(self.imei, dates[0], dates[1], dates[2])
			fuel_economy.generate()
			return JsonResponse({'message':'Fuel Economy Generated Successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Invalid request, IMEI and Date required', 'status':False, 'status_code':400}, status=200)



class FuelEconomyManualGenerate:

	def __init__(self, imei, day, month, year):
		self.imei = imei
		self.day = day
		self.month = month
		self.year = year
		self.fuel_capacity = self.get_fuel_capacity(imei)


	def generate(self):
		timezone = self.get_time_zone(self.imei)
		fuel_economy_list = []
		fuel_emission_list = []
		if timezone:
			time_to_start, time_to_end = self.get_date_to_filter(timezone, self.day,self. month, self.year)
			data = self.get_data(self.imei, time_to_start, time_to_end)
			if self.fuel_capacity:
				for d in data:
					if d.get('journey_fuel_consumption') and d.get('trip_mileage'):
						fuel_capacity_per = (float(d.get('journey_fuel_consumption'))/100)*self.fuel_capacity
						fuel_economy_per_km = 1/fuel_capacity_per
						fuel_economy_list.append(d.get('trip_mileage')*fuel_economy_per_km)
						fuel_emission_list.append(fuel_capacity_per)
			if fuel_economy_list:
				final_fuel_economy = sum(fuel_economy_list)/len(fuel_economy_list)
				self.save_fuel_economy(self.imei, time_to_start.date(), final_fuel_economy)

			if fuel_emission_list:
				self.save_fuel_emission(self.imei, time_to_start.date(), fuel_emission_list)
		pass


	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			self.customer_id = sub.customer_id
			try:
				user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
				if user:
					return user.time_zone
			except(Exception)as e:
				print(e)
				return None
		return None

	def save_fuel_economy(self, imei, date, fuel_economy):
		if fuel_economy:
			if fuel_economy>0:
				fuel_event = FuelEconomy.objects.filter(imei=imei, record_date=date).all()
				if fuel_event:
					fuel_event.delete()
				voltage_obj = {
					'imei': imei,
					'fuel_economy': fuel_economy,
					'record_date':date,
					'customer_id':self.customer_id
				}
				serializer = FuelEconomySerializer(data=voltage_obj)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
		pass


	def save_fuel_emission(self, imei, date, emission):
		if emission:
			emission_obj = Emission.objects.filter(imei=imei, record_date=date).all()
			if emission_obj:
				emission_obj.delete()

			economy = sum(emission)*8.8
			voltage_obj = {
				'imei': imei,
				'emission': economy,
				'record_date':date,
				'customer_id':self.customer_id
			}
			serializer = EmissionSerializer(data=voltage_obj)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()
		pass


	def get_data(self, imei, time_date_start, time_date_end):
		try:
			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()
		except(Exception)as e:
			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()

		stt_serializer = EngineSummarySerializer(stt, many=True).data
		data = [dict(i) for i in stt_serializer]
		records = sorted(data, key = lambda i: i['send_time'],reverse=False)
		return records

	def get_fuel_capacity(self, imei):
		fuel = SettingsModel.objects.filter(imei=imei).last()
		if fuel:
			if fuel.fuel_capacity:
				return fuel.fuel_capacity
			return None
		return None


	def get_date_to_filter(self, timezone, day, month, year):
		timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', date_time_fmt)
		old_timezone = pytz.timezone(timezone)

		new_timezone = pytz.timezone("UTC")
		my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
		timestamp_end = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', date_time_fmt)
		old_timezone_end = pytz.timezone(timezone)
		new_timezone_end = pytz.timezone("UTC")
		my_timestamp_in_new_timezone_end = old_timezone_end.localize(timestamp_end).astimezone(new_timezone_end)
		return my_timestamp_in_new_timezone, my_timestamp_in_new_timezone_end




def fuel_event_module(args):
	trip_id = args
	fuel_event = FuelEventsMachine(trip_id)
	fuel_event.receive_trip_event()


class FuelEventsMachine:
	def __init__(self, trip_id):
		self.trip_id = trip_id
		self.imei = None

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
				fuel_event = FuelEconomy.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)


			# starting_fuel_cunsumption = trip_logs[0][0].get('')
			start_trip_log = trip_logs[0]
			end_trip_log = trip_logs[-1]

			if start_trip_log[0].get('fuel_consumption'):
				start_fuel = start_trip_log[0].get('fuel_consumption')
			else:
				start_fuel = start_trip_log[1].get('fuel_consumption')


			if end_trip_log[-1].get('fuel_consumption'):
				end_fuel = end_trip_log[-1].get('fuel_consumption')
			else:
				end_fuel = end_trip_log[-2].get('fuel_consumption1')


			if start_trip_log[0].get('mileage'):
				start_mileage = start_trip_log[0].get('mileage')
			else:
				start_mileage = start_trip_log[1].get('mileage')


			if end_trip_log[-1].get('mileage'):
				end_mileage = end_trip_log[-1].get('mileage')
			else:
				end_mileage = end_trip_log[-2].get('mileage')

			try:
				fuel_consumed = (float(end_fuel) - float(start_fuel))/1000
			except(Exception)as e:
				fuel_consumed = 0


			try:
				mileage = float(end_mileage) - float(start_mileage)
			except(Exception)as e:
				mileage = 0

			try:
				hd = (1/fuel_consumed)*mileage
				economy = (1/0.264172)*hd
			except(Exception)as e:
				economy = 0


			customer_id = self.get_customer_id(self.imei)
			voltage_obj = {
				'imei': self.imei,
				'fuel_economy': economy,
				'record_date':trip.record_date_timezone.date(),
				'customer_id':customer_id
			}

			serializer = FuelEconomySerializer(data=voltage_obj)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()


	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None

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