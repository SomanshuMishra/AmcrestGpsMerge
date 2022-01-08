from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate

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

from app.events.trips import trip_event_module
from app.events.odometer import odometere_event_module
from app.events.fuel_emission import fuel_emission_module

import string
import random
from datetime import datetime, timedelta
import time
import _thread
import pytz

from app.serializers import *
from app.models import *

from listener.models import *
from listener.serializers import *

from app.location_finder import *

from services.models import *

# from=2020-09-01&to=2020-09-10&category=gps

class TripDeleteApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		range_from = request.data.get('from')
		range_to = request.data.get('to')
		imei = request.data.get('imei', None)
		customer_id = request.data.get('customer_id', None)

		if range_from and range_to and imei:
			record_date_gte = datetime.datetime.strptime(range_from.strip()+" 00:00:00", "%Y-%m-%d %H:%M:%S")
			record_date_lte = datetime.datetime.strptime(range_to.strip()+" 23:59:59", "%Y-%m-%d %H:%M:%S")
			user_trip = UserTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all()
			if user_trip:
				measure_id = [ut.measure_id for ut in user_trip]
				user_trip.delete()
				self.delete_trip_measurements(measure_id)
			return JsonResponse({'message':'Trip Deleted Successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'From Date, To Date and IMEI reqquired', 'status':False, 'status_code':400}, status=400)

	def delete_trip_measurements(self, measure_id):
		trip_measure = TripsMesurement.objects.filter(measure_id__in=measure_id).all()
		trip_measure.delete()
		return True