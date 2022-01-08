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
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q as queue
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import datetime
import datedelta

from .serializers import *
from .models import *

from app.models import *
from app.serializers import *

from user.models import *

from .sim_update_service import *
from .mail_sender import *

import braintree


class DumpUserTrip(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		# print(request.data)
		user_trips = UserTrip.objects.filter(imei=imei).first()
		user_trip = UserTripSerializer(user_trips, many=False)
		return JsonResponse({'message':'User Trip Saved successfull', 'status':True, 'status_code':200, 'user_trip':user_trip.data})


	def post(self, request, imei):
		print(request.data)
		return JsonResponse({'message':'User Trip Saved successfull', 'status':True, 'status_code':200}, status=200)