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
import time

from .serializers import *
from .models import *

from app.models import *
from user.models import *

from .sim_update_service import *
from .mail_sender import *

import braintree




# gateway = braintree.BraintreeGateway(
#                 braintree.Configuration(
#                     braintree.Environment.Sandbox,
#                     merchant_id=settings.BRAINTREE_MERCHANT,
#                     public_key=settings.BRAINTREE_PUBLIC_KEY,
#                     private_key=settings.BRAINTREE_PRIVATE_KEY
#                 )
#             )

gateway = braintree.BraintreeGateway(
                braintree.Configuration( 
                    environment=braintree.Environment.Production, 
                    merchant_id=settings.PRODUCTION_BRAINTREE_MERCHANT, 
                    public_key=settings.PRODUCTION_BRAINTREE_PUBLIC_KEY, 
                    private_key=settings.PRODUCTION_BRAINTREE_PRIVATE_KEY 
                )
            )


class WebHookView(APIView):
	permission_classes = (AllowAny,)
	parser_classes = (JSONParser, FormParser, MultiPartParser,)
	def __init__(self):
		self.subscription_id = None
		self.kind = None
		self.webhook_date_recieved = None


	def post(self, request):
		# print(request.data['bt_signature'])
		self.host = request.META['HTTP_HOST']
		# sample_notification = gateway.webhook_testing.sample_notification(
		#     braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully,
		#     "jc7rgb"
		# )
		
		webhook_notification = gateway.webhook_notification.parse(
		  str(request.data['bt_signature']),
		  request.data['bt_payload']
		)
		
		time.sleep(2)
		# webhook_notification = gateway.webhook_notification.parse(
		#   str(sample_notification['bt_signature']),
		#   sample_notification['bt_payload']
		# )

		if webhook_notification:
			save_webhook = {}
			try:
				self.webhook_date_recieved = save_webhook['webhook_date_recieved'] = webhook_notification.timestamp
				self.kind = save_webhook['kind'] = webhook_notification.kind
				self.subscription_id = save_webhook['subscription_id'] = webhook_notification.subscription.id
			except(Exception) as e:
				self.webhook_date_recieved = None
				self.kind = None
				self.subscription_id = None
				return JsonResponse({'message':'webhook', 'status':True, 'status_code':200}, status=200)

			self.write_webhook_log()
			serializer = WebhookSubscriptionSerializer(data=save_webhook)
			if serializer.is_valid():
				serializer.save()

			subscription = Subscription.objects.filter(subscription_id=webhook_notification.subscription.id).first()
			if subscription:
				if subscription.subscription_status != "subscription_cancel_request":
					subscription.subscription_status = webhook_notification.kind
					subscription.save()

					if webhook_notification.kind == 'subscription_canceled':
						self.subscription_canceled_valuation()
					elif webhook_notification.kind=='subscription_charged_successfully' or webhook_notification.kind=='subscription_went_active':
						
						end_date = webhook_notification.timestamp + datedelta.MONTH
						self.subscription_charged_successfully_valuation(webhook_notification.timestamp, end_date)

					elif webhook_notification.kind=='subscription_charged_unsuccessfully':
						self.subscription_charged_unsuccessfully_valuation()
				else:
					subscription.subscription_status = webhook_notification.kind
					subscription.save()

					if webhook_notification.kind == 'subscription_canceled':
						self.subscription_canceled_valuation_wemail()

		return JsonResponse({'message':'webhook', 'status':True, 'status_code':200}, status=200)

	def write_webhook_log(self):
		try:
			file_name = '/var/www/html/webhook/webhook_'+str(datetime.datetime.now().day)+str(datetime.datetime.now().month)+str(datetime.datetime.now().year)+'.txt'
			file = open(file_name, 'a+')
			date = self.webhook_date_recieved.strftime('%d-%m-%Y %H:%M:%S')
			file.write("Date Time : "+date+", Subscription ID : "+self.subscription_id+", Kind : "+self.kind+'\n')
			file.close()
		except(Exception)as e:
			pass


	def subscription_charged_unsuccessfully_valuation(self):
		get_subscription = Subscription.objects.filter(subscription_id=self.subscription_id).last()
		if get_subscription:
			self.customer_id = get_subscription.customer_id
			self.email = self.get_user_mail(self.customer_id)
			payment_failure_mail([self.email, self.host, self.customer_id, get_subscription.imei_no])

	def subscription_charged_successfully_valuation(self, start_date, end_date):
		get_subscription = Subscription.objects.filter(subscription_id=self.subscription_id).last()
		if get_subscription:
			get_subscription.start_date = start_date
			get_subscription.end_date = end_date
			get_subscription.save()

	def subscription_canceled_valuation(self):
		get_subscription = Subscription.objects.filter(subscription_id=self.subscription_id, subscription_status='subscription_canceled').last()
		if get_subscription:
			if not self.check_plan_updated():
				self.iccid = get_subscription.imei_iccid
				self.imei = get_subscription.imei_no
				self.customer_id = get_subscription.customer_id
				self.email = self.get_user_mail(self.customer_id)
				sim_deactivate_immeidiate_request(self.imei)
				get_subscription.sim_status = False
				get_subscription.device_listing = False
				get_subscription.save()
				subscription_cancel_mail([self.imei, self.email, self.host, self.customer_id])


	def subscription_canceled_valuation_wemail(self):
		get_subscription = Subscription.objects.filter(subscription_id=self.subscription_id, subscription_status='subscription_canceled').last()
		if get_subscription:
			if not self.check_plan_updated():
				self.iccid = get_subscription.imei_iccid
				self.imei = get_subscription.imei_no
				self.customer_id = get_subscription.customer_id
				self.email = self.get_user_mail(self.customer_id)
				# sim_deactivate_immeidiate_request(self.imei)
				get_subscription.sim_status = False
				get_subscription.save()


	def check_plan_updated(self):
		check_subscription_id = SimPlanUpdatedRecord.objects.filter(subscription_id=self.subscription_id).first()
		if check_subscription_id:
			check_subscription_id.delete()
			return True
		return False




	def get_user_mail(self, customer_id):
		user = User.objects.filter(customer_id=customer_id, subuser=False).first()
		if user:
			return user.email
		return None
			