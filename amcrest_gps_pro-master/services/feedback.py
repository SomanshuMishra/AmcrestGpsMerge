from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate

from django.template.loader import render_to_string

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
import datetime
import asyncio
import base64
import hashlib

from datetime import datetime, timedelta

from user.models import *
from user.serializers import *

from app.serializers import *
from app.models import *

from services.models import *
from services.serializers import *
from services.sim_update_service import *
from services.helper import *
from services.mail_sender import *

import braintree


class FeedBackSkippedApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		email = request.data.get('email', None)
		category = request.GET.get('category', None)
		if email and category:
			serializer = FeedBackSkippedSerializer(data={'email':email, 'category':category})
			if serializer.is_valid():
				serializer.save()
				return JsonResponse({'message':'Feedback Skipped', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid Data', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Email and Category Required', 'status':False, 'status_code':400}, status=200)



class ValidateEmailApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		email = request.data.get('email', None)
		user = User.objects.filter(email=email, is_dealer=False, is_dealer_user=False, subuser=False).last()
		category = request.GET.get('category', 'obd')
		if user:
			feedback = FeedBackModel.objects.filter(email=email).last()
			if feedback:
				return JsonResponse({'message':'User already gave feedback', 'status':False, 'status_code':800}, status=200)
			else:
				skipped = FeedBackSkipped.objects.filter(email=email, category=category).last()
				if skipped:
					last_date = datetime.datetime.now() - datetime.timedelta(days = 60)
					if skipped.created_date.replace(tzinfo=None) < last_date:
						return JsonResponse({'message':'Valid User', 'status':True, 'status_code':200}, status=200)
					else:
						return JsonResponse({'message':'Invalid User', 'status':False, 'status_code':400}, status=200)
				else:
					return JsonResponse({'message':'Valid User', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Invalid User', 'status':False, 'status_code':400}, status=200)

class CheckRegisteredDate(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		email = request.data.get('email', None)
		last_date = datetime.datetime.now() - datetime.timedelta(days = 60)
		category = request.GET.get('category', None)

		free_trial_process = AppConfiguration.objects.filter(key_name='free_trial_process').last()
		if not free_trial_process:
			return JsonResponse({'message':'Free Trial process has been deactivated for time being', 'status':False, 'status_code':400}, status=200)
		
		if free_trial_process:
			if not free_trial_process.key_value == 'yes' and not free_trial_process.key_value == 'Yes':
				# print(free_trial_process.key_value)
				return JsonResponse({'message':'Free Trial process has been deactivated for time being', 'status':False, 'status_code':400}, status=200)
			pass
		pass
		
		if category:
			user = User.objects.filter(email=email, subuser=False, date_joined__lte=last_date, is_dealer=False, is_dealer_user=False).last()
			if user:
				feedback = FeedBackModel.objects.filter(email=email, category=category).last()
				if feedback:
					return JsonResponse({'message':'User already gave feedback', 'status':False, 'status_code':400}, status=200)
				else:
					if self.check_trip(user.customer_id):
						# skipped = FeedBackSkipped.objects.filter(email=email).last()
						# if skipped:
						# 	skipped.delete()
						# return JsonResponse({'message':'User registered 45 days ago', 'status':True, 'status_code':200}, status=200)
						skipped = FeedBackSkipped.objects.filter(email=email, category=category).last()
						if skipped:
							last_date = datetime.datetime.now() - datetime.timedelta(days = 60)
							if skipped.created_date.replace(tzinfo=None) < last_date:
								skipped.delete()
								return JsonResponse({'message':'User registered 45 days ago', 'status':True, 'status_code':200}, status=200)
							else:
								return JsonResponse({'message':'Invalid User', 'status':False, 'status_code':400}, status=200)
						else:
							return JsonResponse({'message':'User registered 45 days ago', 'status':True, 'status_code':200}, status=200)
					return JsonResponse({'message':'User registered 45 days ago, but trips not enough', 'status':False, 'status_code':400}, status=200)
			return JsonResponse({'message':'User not registered 45 days ago', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)


	def check_trip(self, customer_id):
		subs = Subscription.objects.filter(is_active=True, device_in_use=True, device_listing=True, customer_id=customer_id).all()
		if subs:
			today = datetime.datetime.now()
			last_month = datetime.datetime.now() - timedelta(days=60)
			for sub in subs:
				if sub.device_model == 'gl300m':
					try:
						customer_id = str(sub.customer_id)
					except(Exception)as e:
						customer_id = None

					user_trip = UserTrip.objects.filter(imei=sub.imei_no, customer_id=customer_id, record_date_timezone__lte=today, record_date_timezone__gte=last_month).all()
					# print(user_trip, len(user_trip), sub.imei_no)
					if len(user_trip) >= 20:
						return True
					else:
						pass
		return False


class PositiveFeedbackApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		request.data['positive'] = True
		request.data['category'] = request.GET.get('category', None)
		if request.data['category']:
			serializer = FeedBackPositiveSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				positive_feedback_mail_sender(request.data.get('email', None), request.data)
				return JsonResponse({'message':'Feedback Submitted Successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Error During Feedback Submit', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)

class NegativeFeedbackApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		request.data['category'] = request.GET.get('category', None)
		if request.data['category']:
			serializer = FeedBackNegativeSerializers(data=request.data)
			if serializer.is_valid():
				serializer.save()
				negative_feedback_support_mail(request.data.get('email', None), request.data)
				negative_feedback_mail_sender(request.data.get('email', None), request.data)
				return JsonResponse({'message':'Feedback Submitted Successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Error During Feedback Submit', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)