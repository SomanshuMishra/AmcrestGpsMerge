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
from datetime import timedelta
import asyncio
import base64
import hashlib

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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


class ReviewSystemValidation(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id):
		category = request.GET.get('category', None)
		if category:
			last_15_days = datetime.datetime.now() - timedelta(days=45)
			subscription = Subscription.objects.filter(record_date__lte=last_15_days, device_in_use=True, is_active=True, customer_id=customer_id).first()
			if subscription:
				review = ReviewTable.objects.filter(customer_id=customer_id, category=category).last()
				if not review:
					return JsonResponse({'message':'Valid for review', 'status':True, 'show':True, 'status_code':200}, status=200)

				if review:
					if review.eligible:
						if review.count:
							review_count = review.count
						else:
							review.count = 1
							review.save()
							review_count = 1

						if review_count<3:
							if review.eligible:
								try:
									if review.next_review_date<=datetime.datetime.now():
										return JsonResponse({'message':'Valid for review', 'status':True, 'show':True, 'status_code':200}, status=200)
									return JsonResponse({'message':'Not valid for review', 'status':True, 'show':False, 'status_code':200}, status=200)
								except(Exception)as e:
									return JsonResponse({'message':'Valid for review', 'status':True, 'show':True, 'status_code':200}, status=200)
							return JsonResponse({'message':'Not valid for review', 'status':True, 'show':False, 'status_code':200}, status=200)
						return JsonResponse({'message':'Not valid for review', 'status':True, 'show':False, 'status_code':200}, status=200)
					return JsonResponse({'message':'Not valid for review', 'status':True, 'show':False, 'status_code':200}, status=200)
				return JsonResponse({'message':'valid for review', 'status':True, 'show':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Not valid for review', 'status':True, 'show':False, 'status_code':200}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)



class ReviewSkipped(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id):
		category = request.GET.get('category', None)
		if category:
			review = ReviewTable.objects.filter(customer_id=customer_id, category=category).last()
			if review:
				if review.count:
					review.count = review.count + 1
				else:
					review.count = 1

				next_7_days = datetime.datetime.now() + timedelta(days=30)

				review.next_review_date = next_7_days.date()
				review.save()
				return JsonResponse({'message':'Review Skipped', 'status':True, 'status_code':200}, status=200)
			else:
				next_7_days = datetime.datetime.now() + timedelta(days=30)
				review_dict = {
					'customer_id':customer_id,
					'next_review_date':next_7_days.date(),
					'count':1,
					'eligible':True,
					'category':category
				}
				serializer = ReviewTableSerializer(data=review_dict)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({'message':'Review Skipped', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)


class ReviewRating(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		category = request.GET.get('category', None)
		if category:
			rating = request.data.get('rating', None)
			next_7_days = datetime.datetime.now() + timedelta(days=30)
			customer_id = request.data.get('customer_id', None)
			if customer_id:
				if rating:
					if rating>3:
						review = ReviewTable.objects.filter(customer_id=customer_id, category=category).last()
						if review:
							if review.count: 
								review.count = review.count + 1
							else:
								review.count = 1

							review.rating = rating
							review.comments = request.data.get('comments', None)
							review.next_review_date = next_7_days.date()
							review.save()
						else:
							review_dict = {
								'customer_id':customer_id,
								'next_review_date':next_7_days.date(),
								'count':1,
								'comments':request.data.get('comments', None),
								'rating':rating,
								'eligible':True,
								'category':category
							}
							serializer = ReviewTableSerializer(data=review_dict)
							if serializer.is_valid():
								serializer.save()
						review_rating_more([customer_id, request.data.get('comments', ''), rating])
						return JsonResponse({'message':'Review Rating Saved Successfully', 'status':True, 'status_code':200}, status=200)
					else:
						review = ReviewTable.objects.filter(customer_id=customer_id, category=category).last()
						if review:
							if review.count: 
								review.count = review.count + 1
							else:
								review.count = 1

							review.rating = rating
							review.comments = request.data.get('comments', None)
							review.next_review_date = next_7_days.date()
							review.save()
						else:
							review_dict = {
								'customer_id':customer_id,
								'next_review_date':next_7_days.date(),
								'count':1,
								'comments':request.data.get('comments', None),
								'rating':rating,
								'eligible':True,
								'category':category
							}
							serializer = ReviewTableSerializer(data=review_dict)
							if serializer.is_valid():
								serializer.save()
						review_rating_less([customer_id, request.data.get('comments', ''), rating])
						
						return JsonResponse({'message':'Review Rating Saved Successfully', 'status':True, 'status_code':200}, status=200)
				else:
					review = ReviewTable.objects.filter(customer_id=customer_id, category=category).last()
					if review:
						if review.count: 
							review.count = review.count + 1
						else:
							review.count = 1

						review.rating = rating
						review.comments = request.data.get('comments', None)
						review.next_review_date = next_7_days.date()
						review.save()
					else:
						review_dict = {
							'customer_id':customer_id,
							'next_review_date':next_7_days.date(),
							'count':1,
							'comments':request.data.get('comments', None),
							'rating':rating,
							'eligible':True,
							'category':category
						}
						serializer = ReviewTableSerializer(data=review_dict)
						if serializer.is_valid():
							serializer.save()
					review_rating_less([customer_id, request.data.get('comments', ''), rating])
					return JsonResponse({'message':'Review Rating Saved Successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Customer ID required', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)


class ReviewFinal(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id):
		category = request.GET.get('category', None)
		if category:
			review = ReviewTable.objects.filter(customer_id=customer_id, category=category).last()
			if review:
				review.eligible = 0
				review.next_review_date = None
				review.save()
				return JsonResponse({'message':'Review Sent Successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Review Sent Successfully', 'status':False, 'status_code':200}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)