from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate
from django.conf import settings
from geopy.geocoders import Nominatim
from django.db import close_old_connections

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


class GpsEventsDateView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, reqquest, imei, customer_id, event):
		if event == 'notification':
			events = Notifications.objects.filter(imei=imei, customer_id=customer_id).all()
		else:
			events = Notifications.objects.filter(imei=imei, type=event, customer_id=customer_id).all()

		close_old_connections()
		if events:
			serializer = GpsEventsDateSerializer(events, many=True)
			dates = [i.get('record_date_timezone') for i in serializer.data]
			dates = list(set(dates))
			return JsonResponse({'message':'Events Available dates for event '+event, 'status':True, 'status_code':200, 'dates':dates}, status=200)
		return JsonResponse({'message':'Events Available dates for event '+event, 'status':True, 'status_code':200, 'dates':[]}, status=200)


class GpsEventsView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei, customer_id, event):
		request_from_date = request.GET.get('from', None)
		request_to_date = request.GET.get('to', None)
		request_date = request.GET.get('date', None)

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')
			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				if event == 'notification':
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all()
				else:
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, type=event, customer_id=customer_id).all()
				serializer = NotificationsReadSerializer(notifications, many=True)
				close_old_connections()
				return JsonResponse({'message':'Event list', 'from_date':request_from_date, 'to_date':request_to_date, 'events':serializer.data, 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				if event == 'notification':
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all()
				else:
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, type=event, customer_id=customer_id).all()
					
				serializer = NotificationsReadSerializer(notifications, many=True)
				close_old_connections()
				return JsonResponse({'message':'Event list', 'from_date':request_date, 'to_date':request_date, 'events':serializer.data, 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_date, 'to_date':request_date}, status=200)
		close_old_connections()
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'notifications':[]}, status=200)



# class GpsNotificationsEventsDateView(APIView):
# 	permission_classes = (AllowAny,)
# 	def get(self, reqquest, imei):
# 		events = Notifications.objects.filter(imei=imei).all()
# 		if events:
# 			serializer = GpsEventsDateSerializer(events, many=True)
# 			dates = [i.get('record_date_timezone') for i in serializer.data]
# 			dates = list(set(dates))
# 			return JsonResponse({'message':'Notification Available dates for event '+event, 'status':True, 'status_code':200, 'dates':dates}, status=200)
# 		return JsonResponse({'message':'Notification Available dates for event '+event, 'status':True, 'status_code':200, 'dates':[]}, status=200)



# class GpsNotificationsEventsView(APIView):
# 	permission_classes = (AllowAny,)
# 	def get(self, request, imei):
# 		request_from_date = request.GET.get('from', None)
# 		request_to_date = request.GET.get('to', None)
# 		request_date = request.GET.get('date', None)

# 		if request_from_date and request_to_date:
# 			from_date = request_from_date.split('-')
# 			to_date = request_to_date.split('-')
# 			try:
# 				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
# 				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
# 				notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
# 				serializer = NotificationsReadSerializer(notifications, many=True)
# 				return JsonResponse({'message':'Notification list', 'from_date':request_from_date, 'to_date':request_to_date, 'events':serializer.data, 'status':True, 'status_code':200}, status=200)
# 			except(Exception)as e:
# 				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
# 		elif request_date:
# 			try:
# 				from_date = request_date.split('-')
# 				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
# 				record_date_lte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
# 				notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
# 				serializer = NotificationsReadSerializer(notifications, many=True)
# 				return JsonResponse({'message':'Notification list', 'from_date':request_date, 'to_date':request_date, 'events':serializer.data, 'status':True, 'status_code':200}, status=200)
# 			except(Exception)as e:
# 				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_date, 'to_date':request_date}, status=200)
# 		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'notifications':[]}, status=200)
