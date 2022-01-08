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

from support.models import *

from .serializers import *
from app.serializers import *

import braintree


# testmayurid

gateway = braintree.BraintreeGateway(
                braintree.Configuration( 
                    environment=braintree.Environment.Production, 
                    merchant_id=settings.PRODUCTION_BRAINTREE_MERCHANT, 
                    public_key=settings.PRODUCTION_BRAINTREE_PUBLIC_KEY, 
                    private_key=settings.PRODUCTION_BRAINTREE_PRIVATE_KEY 
                )
            )

# gateway = braintree.BraintreeGateway(
#                 braintree.Configuration(
#                     braintree.Environment.Sandbox,
#                     merchant_id=settings.BRAINTREE_MERCHANT,
#                     public_key=settings.BRAINTREE_PUBLIC_KEY,
#                     private_key=settings.BRAINTREE_PRIVATE_KEY
#                 )
#             )


class ApplyFreeTrialApiView(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		old_id = request.data.get('subscription_id', None)
		imei = request.data.get('imei', None)

		subscription = Subscription.objects.filter(subscription_id=old_id).first()
		one_month_ago = datetime.datetime.now() - datedelta.datedelta(months=1)
		
		if old_id:
			new_id = old_id+str(random.randint(0,1000000,))
		else:
			return JsonResponse({'message':'Subscription ID required', 'status':False, 'status_code':400}, status=200)

		try:
			free_trial_months = int(request.data.get('free_trial_month', None))
		except(Exception)as e:
			return JsonResponse({'message':'Free Trial Duration required', 'status':False, 'status_code':400}, status=400)

		

		if old_id and new_id and imei:
			if subscription:
				free_trial = FreeTrialModel.objects.filter(imei=imei, customer_id=subscription.customer_id, update_date__gte=one_month_ago).last()
				if free_trial:
					return JsonResponse({'message':'Cannot Apply Free Trial at this moment. As last Free Trial Applied within last month. ', 'status':False, 'status_code':400}, status=400)

				if self.rename_subscription_id(old_id, new_id):
					if self.cancel_subscription(new_id):
						if subscription:
							subscription_start_date = subscription.end_date + datedelta.datedelta(months=free_trial_months)
							self.customer_id = subscription.customer_id
							if self.generate_client_token():
								if self.create_subscription(subscription, subscription_start_date):
									subscription.start_date = subscription.end_date
									subscription.end_date = subscription_start_date
									subscription.firstBillingDate = subscription_start_date
									subscription.nextBillingDate = subscription_start_date
									subscription.save()
									self.save_free_trial_log(imei, subscription.customer_id, old_id, free_trial_months)
									send_free_trial_mail(subscription.customer_id, subscription_start_date, free_trial_months)
									return JsonResponse({'message':'Free Trial Applied', 'status':True, 'status_code':200}, status=200)
								return JsonResponse({'message':'Error during creating subscription', 'status':False, 'status_code':400}, status=200)
							return JsonResponse({'message':'Error During Generating Payment Token', 'status_code':400, 'status':False}, status=200)
						return JsonResponse({'message':'Invalid Subscription ID', 'status':False, 'status_code':400}, status=200)
					return JsonResponse({'message':'Error During Cancelling Subscription', 'status':False, 'status_code':400}, status=200)
				return JsonResponse({'message':'Error During Updating Subscription ID', 'status':False, 'status_code':400}, status=400)
			return JsonResponse({'message':'Invalid Subscription ID', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Subscription ID and IMEI required', 'status':False, 'status_code':400}, status=200)

	def rename_subscription_id(self, old_id, new_id):
		
		try:
			result = gateway.subscription.update(old_id, {
			    "id": new_id
			})
			if result.is_success:
				return True
			return False
		except(Exception)as e:
			return False

	def save_free_trial_log(self, imei, customer_id, subscription_id, duration):
		free_trial = FreeTrialModel.objects.filter(imei=imei, customer_id=customer_id).last()
		if free_trial:
			free_trial.free_trial_month = duration+free_trial.free_trial_month
			free_trial.save()
		else:
			serializer = FreeTrialSerializer(data={
					'imei':imei,
					'customer_id':customer_id,
					'free_trial_month':duration
				})
			if serializer.is_valid():
				serializer.save()

	def cancel_subscription(self, subscription_id):
		try:
			result = gateway.subscription.cancel(subscription_id)
			if result.is_success:
				return True
			return False
		except(Exception)as e:
			return False


	def create_subscription(self, subscription, start_date):
		
		try:
			result = gateway.subscription.create({
					"id":subscription.subscription_id,
	                "payment_method_token": self.client_token,
	                "plan_id": subscription.activated_plan_id,
	                "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant",
	                "first_billing_date":start_date
	            })
			if result.is_success:
				return True

			return False
		except(Exception)as e:
			print(e)
			return False

	def generate_client_token(self):
		try:
			client_token = gateway.customer.find(str(self.customer_id))
			self.client_token = client_token.credit_cards[0].token
			return True
		except(Exception)as e:
			print(e)
			return None


# class ApplyFreeTrialApiView(APIView):
# 	permission_classes = (AllowAny,)
# 	def post(self, request):
# 		subscription_id = request.data.get('subscription_id', None)
# 		try:
# 			free_trial_months = int(request.data.get('free_trial_month', None))
# 		except(Exception)as e:
# 			return JsonResponse({'message':'Free Trial Duration required', 'status':False, 'status_code':400}, status=400)

# 		subscription = Subscription.objects.filter(subscription_id=subscription_id).first()
# 		if subscription:
# 			subscription_start_date = subscription.end_date + datedelta.datedelta(months=free_trial_months)
# 			self.customer_id = subscription.customer_id
# 			if self.generate_client_token():
# 				if self.create_subscription(subscription, subscription_start_date):
# 					subscription.start_date = subscription.end_date
# 					subscription.end_date = subscription_start_date
# 					subscription.firstBillingDate = subscription_start_date
# 					subscription.nextBillingDate = subscription_start_date
# 					subscription.save()
# 					return JsonResponse({'message':'Free Trial Applied', 'status':True, 'status_code':200}, status=200)
# 				return JsonResponse({'message':'Error during creating subscription', 'status':False, 'status_code':400}, status=200)
# 			return JsonResponse({'message':'Error During Generating Payment Token', 'status_code':400, 'status':False}, status=200)
# 		return JsonResponse({'message':'Invalid Subscription ID', 'status':False, 'status_code':400}, status=200)


# 	def create_subscription(self, subscription, start_date):
		
# 		try:
# 			result = gateway.subscription.create({
# 					"id":subscription.subscription_id,
# 	                "payment_method_token": self.client_token,
# 	                "plan_id": subscription.activated_plan_id,
# 	                # "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant",
# 	                "first_billing_date":start_date
# 	            })
# 			print(result)
# 			if result.is_success:
# 				return True

# 			return False
# 		except(Exception)as e:
# 			print(e)
# 			return False

# 	def generate_client_token(self):
# 		try:
# 			client_token = gateway.customer.find(str(self.customer_id))
# 			self.client_token = client_token.credit_cards[0].token
# 			return True
# 		except(Exception)as e:
# 			print(e)
# 			return None


# first_billing_date