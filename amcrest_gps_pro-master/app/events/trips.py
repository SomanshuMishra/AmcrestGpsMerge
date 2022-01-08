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








class TripEventView(APIView):
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
				trip_instance = TripEvents.objects.filter(imei=imei, date__range=[filter_from_date, filter_to_date], customer_id=customer_id).all().order_by('-date' ,'-time')
				serializer = TripEventsSerializer(trip_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Trip Event details', 'from_date':request_from_date, 'to_date':request_to_date, 'trip_event':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				odometer_instance = TripEvents.objects.filter(imei=imei, date__day=from_date[0], date__month=from_date[1], date__year=from_date[2], customer_id=customer_id).all().order_by('-date','-time')
				serializer = TripEventsSerializer(odometer_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Trip Event details', 'date':request_date, 'trip_event':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'trip_event':[]}, status=200)







# def trip_event_module(trip_id, imei):
# 	trip_event = TripEventsMachine(trip_id, imei)
# 	trip_event.receive_trip_event()

def trip_event_module(args):
	trip_id = args[0]
	trip_event = TripEventsMachine(trip_id)
	trip_event.receive_trip_event()

class TripEventsMachine:
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
				trip_event = TripEvents.objects.filter(imei=self.imei, record_date=trip.record_date.date()).all()
				if trip_event:
					trip_event.delete()
			except(Exception)as e:
				print(e)

			for trip_log in trip_logs:

				start_trip_time = self.format_date(trip_log[0].get('send_time'))
				end_trip_time = self.format_date(trip_log[-1].get('send_time'))
				
				try:
					# self.prepare_trip_event(self.imei, trip_log[0], trip_log[-1], start_trip_time, end_trip_time, trip.record_date)
					_thread.start_new_thread(prepare_trip_event, (self.imei, trip_log[0], trip_log[-1], start_trip_time, end_trip_time, trip.record_date_timezone))
				except(Exception)as e:
					print(e)
					pass
				close_old_connections()
				# time.sleep(1)


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



def get_customer_id(imei):
	customer_id = Subscription.objects.filter(imei_no=imei).last()
	if customer_id:
		return customer_id.customer_id
	return None


def prepare_trip_event(imei, start_trip_obj, end_trip_obj, start_time, end_time, trip_date):
	try:
		start_location = get_location(start_trip_obj.get('longitude', None), start_trip_obj.get('latitude', None))
		end_location = get_location(end_trip_obj.get('longitude', None), end_trip_obj.get('latitude', None))
	except(Exception)as e:
		print(e)
		start_location = 'Unknown'
		end_location = 'Unknown'

	try:
		customer_id = get_customer_id(imei)
	except(Exception)as e:
		print(e)
		customer_id = None
		
	trip_start_obj = {
		'imei':imei,
		'type': 'start_trip',
		'location' : start_location,
		'date' : start_time.date(),
		'time' : start_time.time(),
		'record_date' :trip_date.date(),
		'customer_id' : customer_id
	} 

	save_trip_events(trip_start_obj)

	trip_end_obj = {
		'imei':imei,
		'type': 'end_trip',
		'location' : end_location,
		'date' : end_time.date(),
		'time' : end_time.time(),
		'record_date' :trip_date.date(),
		'customer_id' : customer_id
	}
	save_trip_events(trip_end_obj)


def save_trip_events(event):
	serializer = TripEventsSerializer(data=event)
	if serializer.is_valid():
		serializer.save()
	else:
		print(serializer.errors)
	close_old_connections()