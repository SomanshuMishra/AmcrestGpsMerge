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


harsh_type_details = {
	"00":"Unknow speed harsh breaking behaviour",
	"01": "Unknow speed harsh acceleration behaviour",
	"02": "Unknow speed harsh turning behaviour",
	"03": "unknow speed harsh braking and turning behaviour",
	"04": "unknow speed harsh acceleration and turning behaviour",
	"05": "unknow speed unknown harsh_behaviour",

	"10": "low speed harsh breaking behaviour",
	"11": "low speed harsh accesleration behaviour",
	"12": "low speed harsh turning behaviour",
	"13": "low speed harsh braking and turning behaviour",
	"14": "low speed harsh acceleration and turning behaviour",
	"15": "low speed unknown harsh behaviour",

	"20": "medium speed harsh breaking behaviour",
	"21": "medium speed harsh accesleration behaviour",
	"22": "medium speed harsh turning behaviour",
	"23": "medium speed harsh braking and turning behaviour",
	"24": "medium speed harsh acceleration and turning behaviour",
	"25": "medium speed unknown harsh behaviour",

	"30": "high speed harsh breaking behaviour",
	"31": "high speed harsh accesleration behaviour",
	"32": "high speed harsh turning behaviour",
	"33": "high speed harsh braking and turning behaviour",
	"34": "high speed harsh acceleration and turning behaviour",
	"35": "high speed unknown harsh behaviour",
}


def harsh_event_receiver(imei, details):
	harsh_event = HarshEventMachine(imei, details)
	harsh_event.receive_harsh_event()


class HarshEventMachine:
	def __init__(self, imei, details):
		self.imei = imei
		self.details = details

	def receive_harsh_event(self):
		try:
			time_zone = self.get_time_zone(self.imei)
			time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
			date_to_be_send = time_timezone.strftime("%Y-%m-%d")
		except(Exception)as e:
			time_timezone = datetime.datetime.now()
			date_to_be_send = time_timezone.strftime("%Y-%m-%d %H:%M:%d")

		try:
			harsh_type = harsh_type_details.get(self.details.get('report_type'))
		except(Exception)as e:
			harsh_type = 'Harsh Behaviour'

		try:
			customer_id = self.get_customer_id(self.imei)
		except(Exception)as e:
			customer_id = None

		self.save_harsh_event(self.imei, harsh_type, date_to_be_send, time_timezone, customer_id)
		close_old_connections()

	
	def save_harsh_event(self, imei, harsh_type, date, time_timezone, customer_id):
		harsh_obj = {
			'imei':imei,
			'harsh_type':harsh_type,
			'record_date':date,
			'record_time':time_timezone.time(),
			'customer_id':customer_id
		}
		serializer = HarshEventSerializer(data=harsh_obj)
		if serializer.is_valid():
			serializer.save()
			close_old_connections()


	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
			close_old_connections()
			if user.time_zone:
				return user.time_zone
		close_old_connections()
		return 'UTC'

	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None




class HarshEventView(APIView):
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
				harsh_instance = HarshBehaviourEvent.objects.filter(imei=imei, record_date__range=[filter_from_date, filter_to_date], customer_id=customer_id).all().order_by('-record_date', '-record_time')
				serializer = HarshEventSerializer(harsh_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Harsh Events details', 'from_date':request_from_date, 'to_date':request_to_date, 'harsh_event':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				harsh_instance = HarshBehaviourEvent.objects.filter(imei=imei, record_date__day=from_date[0], record_date__month=from_date[1], record_date__year=from_date[2], customer_id=customer_id).all().order_by('-record_date', '-record_time')
				serializer = HarshEventSerializer(harsh_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Harsh Events details', 'date':request_date, 'harsh_event':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'date':request_date}, status=200)
		close_old_connections()
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'harsh_event':[]}, status=200)