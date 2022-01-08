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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import datetime
import datedelta
import asyncio


from twilio.rest import Client
from django.conf import settings

from listener.models import *
from listener.serializers import *

from app.models import *
from app.serializers import *

from user.models import *
from user.serializers import *

from services.sim_update_service import *
from services.mail_sender import *
from services.models import *
from services.helper import *
from services.serializers import *

from app.models import *
from user.models import *

from .serializers import *

import braintree

from support.data_loader import user_loader, subscription_loader, zone_loader, setting_loader, report_loader

class UserLoaderApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			customer_id = request.data.get('customer_id')
			if customer_id:
				result = user_loader.load_user(customer_id)
				return JsonResponse({'message':'User Loader', 'status':True, 'status_code':200, 'result':result}, status=200)
			return JsonResponse({'message':'Customer ID Required', 'status':False, 'status_code':False}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':False}, status=400)


class SubscriptionLoaderApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			customer_id = request.data.get('customer_id')
			if customer_id:
				result = subscription_loader.load_subscription(customer_id)
				return JsonResponse({'message':'Subscription Loader', 'status':True, 'status_code':200, 'result':result}, status=200)
			return JsonResponse({'message':'Customer ID Required', 'status':False, 'status_code':False}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':False}, status=400)



class ZoneLoaderApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			customer_id = request.data.get('customer_id')
			if customer_id:
				result = zone_loader.load_zone(customer_id)
				return JsonResponse({'message':'Zone Loader', 'status':True, 'status_code':200, 'result':result}, status=200)
			return JsonResponse({'message':'Customer ID Required', 'status':False, 'status_code':False}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':False}, status=400)


class SettingLoaderApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			customer_id = request.data.get('customer_id')
			if customer_id:
				result = setting_loader.load_setting(customer_id)
				return JsonResponse({'message':'Zone Loader', 'status':True, 'status_code':200, 'result':result}, status=200)
			return JsonResponse({'message':'Customer ID Required', 'status':False, 'status_code':False}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':False}, status=400)


class ReportLoaderApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			customer_id = request.data.get('customer_id')
			if customer_id:
				result = report_loader.load_report(customer_id)
				return JsonResponse({'message':'Report Loader', 'status':True, 'status_code':200, 'result':result}, status=200)
			return JsonResponse({'message':'Customer ID Required', 'status':False, 'status_code':False}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':False}, status=400)