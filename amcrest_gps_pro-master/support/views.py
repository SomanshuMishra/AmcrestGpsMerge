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


User = get_user_model()


class SupportUserView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		page = request.GET.get('page', 1)

		end = int(page)*50
		start = end-50

		query = request.GET.get('query', None)

		if query:
			sub_filter = queue(imei_no__icontains=query) | queue(imei_iccid__icontains=query) | queue(subscription_status__icontains=query) | queue(subscription_id__icontains=query) | queue(customer_id__icontains=query)
			user_filter = queue(first_name__icontains=query) | queue(last_name__icontains=query) | queue(email__icontains=query) | queue(customer_id__icontains=query) | queue(country__icontains=query)
			users = User.objects.filter(user_filter).values('customer_id').distinct()
			subs = Subscription.objects.filter(sub_filter).values('customer_id').distinct()
			
			customer_ids = [i.get('customer_id') for i in users]
			subs_ids = [i.get('customer_id') for i in subs]

			main_list = list(dict.fromkeys(customer_ids+subs_ids))
			user = User.objects.filter(customer_id__in=customer_ids+subs_ids).order_by('-id')[start:end]
			serializer = SupportUserSerializer(user, many=True)
			return JsonResponse({'message':'List of user', 'status':True, 'status_code':200, 'customers':serializer.data, 'total_user':len(main_list)}, status=200)

		user = User.objects.all().order_by('-id')[start:end]
		serializer = SupportUserSerializer(user, many=True)
		return JsonResponse({'message':'List of user', 'status':True, 'status_code':200, 'customers':serializer.data, 'total_user':User.objects.count()}, status=200)


class GetSimStatus(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		if imei:
			sim_status = get_sim_status(imei)
			return JsonResponse({'message':'Sim status', 'status':True, 'status_code':200, 'sim_status':sim_status}, status = 200)
		return JsonResponse({'message':'Invalid request', 'status_code':400, 'status':False}, status=400)


class SupportEmailUpdate(APIView):
	# permission_classes = (AllowAny,)
	def put(self, request):
		if request.data:
			id = request.data.get('id', None)
			email = request.data.get('email', None)

			if id and email:
				user = User.objects.filter(id=id).first()
				if user:
					user.email = email
					user.save()
					return JsonResponse({'message':'User Email updated successfully', 'status':True, 'status_code':204}, status=200)
				return JsonResponse({'message':'Invalid user details, User not found', 'status':False, 'status_code':404}, status=404)
			return JsonResponse({'message':'User ID and Email required', 'status':False, 'status_code':400}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)


class SupportPasswordUpdate(APIView):
	# permission_classes = (AllowAny,)
	def put(self, request):
		if request.data:
			id = request.data.get('id', None)
			password = request.data.get('password', None)

			if id and password:
				user = User.objects.filter(id=id).first()
				if user:
					user.password = make_password(password)
					user.save()
					return JsonResponse({'message':'User password updated successfully', 'status':True, 'status_code':204}, status=200)
				return JsonResponse({'message':'Invalid user details, User not found', 'status':False, 'status_code':404}, status=404)
			return JsonResponse({'message':'User ID and Password required', 'status':False, 'status_code':400}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)


class ReturnDeviceView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.user = None
		self.subscription_instance = None
		self.request_data = None

	def post(self, request):
		host = request.META['HTTP_HOST']
		if request.data:
			imei = request.data.get('imei', None)
			if imei:
				self.subscription_instance = subscription_instance = Subscription.objects.filter(imei_no=imei, device_in_use=True).last()
				if self.subscription_instance:
					if self.cancel_subscription(self.subscription_instance.subscription_id):
						self.customer_id = self.subscription_instance.customer_id
						self.subscription_instance.is_active = False
						self.subscription_instance.subscription_status = 'Subscription Cancel/Device Return Request'
						self.subscription_instance.sim_status = False
						self.subscription_instance.imei_no = imei+'-'+str(self.subscription_instance.customer_id)
						self.subscription_instance.device_in_use = False
						self.subscription_instance.device_listing = False
						self.subscription_instance.save()

						sim_deactivate_immeidiate_request(imei)

						request.data['customer_id'] = str(self.subscription_instance.customer_id)
						request.data['start_date'] = self.subscription_instance.start_date
						request.data['end_date'] = self.subscription_instance.end_date
						request.data['subscription_id'] = self.subscription_instance.subscription_id
						request.data['iccid'] = self.subscription_instance.imei_iccid

						self.update_setting(imei, self.customer_id)

						user_details = self.prepare_details()
						loop = asyncio.new_event_loop()
						loop.run_in_executor(None, device_return_mail, [self.user.id, host, self.subscription_instance.id, request.data, user_details])
						Subscription.objects.filter(imei_no=imei).update(imei_no=imei+'-'+str(self.subscription_instance.customer_id))
						return JsonResponse({'message':'Device Subscription cancelled', 'status':True, 'status_code':200}, status=200)
					return JsonResponse({'message':'Error during cancelling subscription please contact support', 'status':False, 'status_code':400}, status=400)
				return JsonResponse({'message':'Invalid Email or IMEI', 'status':False, 'status_code':404}, status=404)
			return JsonResponse({'message':'Required IMEI, Bad Request', 'status':False, 'status_code':400}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)


	def cancel_subscription(self, subscription_id):
		try:
			result = gateway.subscription.cancel(subscription_id)
			if result.is_success:
			    return True
			return True
		except(Exception)as e:
			return True

	def prepare_details(self):
		self.user = User.objects.filter(customer_id=self.customer_id, subuser=False).last()
		if self.user:
			serializer = UserSerialzer(self.user)
			return serializer.data
		return {}

	def update_setting(self, imei, customer_id):
		setting_update = SettingsModel.objects.filter(imei=imei).last()
		if setting_update:
			# setting_update.imei = str(imei)+'-'+str(customer_id)
			# setting_update.save()
			setting_update.delete()
		pass


class ResendActivationMailView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request, user_id):
		host = request.META['HTTP_HOST']
		user = User.objects.filter(id=user_id).first()
		password = request.data.get('password', 'amcrestgps')
		category = request.GET.get('category', 'gps')

		if user:
			user.password = user.hash_password(password)
			user.save()
			# print('start_sending', category)
			loop = asyncio.new_event_loop()
			loop.run_in_executor(None, resend_registration_mail, [user.id, host, password, category])
			return JsonResponse({'message':'Resent activation Mail', 'status_code':200, 'status':True}, status=200)
		return JsonResponse({'message':'Invalid User', 'status':False, 'status_code':404}, status=404)




	def generate_password(self):
		return ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))


class DeactivateSimView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		subscription_instance = Subscription.objects.filter(imei_no=imei).last()
		if subscription_instance:
			if True:
				if sim_deactivate_immeidiate_request(imei):
					subscription_instance.sim_status = False
					subscription_instance.device_listing = False
					subscription_instance.save()
					return JsonResponse({'message':'Sim Deactivated Successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'Error during deactivating Sim', 'status':False, 'status_code':400}, status=400)
			else:
				subscription_instance.sim_status = False
				subscription_instance.device_listing = False
				subscription_instance.save()
				return JsonResponse({'message':'Sim Deactivated Successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Sim already Deactivated', 'status_code':200, 'status':False}, status=200)
		return JsonResponse({'message':'Invalid IMEI, please provide Valid IMEI', 'status':'False', 'status_code':404}, status=404)


class ActivateSimView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		subscription_instance = Subscription.objects.filter(imei_no=imei, device_in_use=True).last()
		if subscription_instance:
			if subscription_instance.sim_status == False:
				if sim_activate_immeidiate_request(imei):
					subscription_instance.sim_status = True
					subscription_instance.device_listing = True
					subscription_instance.save()
					return JsonResponse({'message':'Sim Activated Successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'Error during activating Sim', 'status':False, 'status_code':400}, status=400)
			return JsonResponse({'message':'Sim already Activated', 'status_code':200, 'status':False}, status=200)
		return JsonResponse({'message':'Invalid IMEI, please provide Valid IMEI', 'status':'False', 'status_code':404}, status=404)


class MasterPasswordView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		pwd = AppConfiguration.objects.filter(key_name='master_password').first()
		if pwd:
			return JsonResponse({'message':'Master Password', 'status_code':200, 'status':True, 'master_password':pwd.base64_value}, status=200)
		return JsonResponse({'message':'Cannot get password', 'status_code':404, 'status':False}, status = 404)


class MessageSenderView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		number = request.data.get('number', None)
		message = request.data.get('message', None)
		if number and message:
			if self.send_sms(message, number):
				return JsonResponse({'message':'Message sent', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid Number, Error during sending message', 'status_code':400, 'status':True}, status=400)
		return JsonResponse({'message':'Number And Message required', 'status':False, 'status_code':400}, status=400)

	def send_sms(self, message_body, number):
		client = Client(self.get_twilio_sid(), self.get_twilio_token())
		# client = Client("AC7f0106ada2e3c2f8f745f6b2c4752f47", "d18c56acfa4ddf441faf0ef8564453d4")
		try:
			message = client.messages.create(
					to = number,
					from_ = "+1832-648-2815",
					body = message_body
				)
			if not message.error_code:
				return True
			return False
		except(Exception)as e:
			return False

	def get_twilio_sid(self):
		app_conf = AppConfiguration.objects.filter(key_name='twilio_sid').first()
		if app_conf:
			return app_conf.key_value
		return settings.TWILIO_SID


	def get_twilio_token(self):
		app_conf = AppConfiguration.objects.filter(key_name='twilio_token').first()
		if app_conf:
			return app_conf.key_value
		return settings.TWILIO_TOKEN


	def get_twilio_from_number(self):
		app_conf = AppConfiguration.objects.filter(key_name='twilio_from_number').first()
		if app_conf:
			return app_conf.key_value
		return settings.TWILIO_FROM_NUMBER



class ActivatedDeviceCountView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		request_from_date = request.data.get('from', None)
		request_to_date = request.data.get('to', None)

		if request_from_date and request_to_date:

			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')

			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
			except(Exception)as e:
				return JsonResponse({'message':'Please Choose proper date', 'status_code':400, 'status':False}, status=400)

			try:
				device = Subscription.objects.filter(firstBillingDate__gte=record_date_gte, record_date__gte=record_date_gte,firstBillingDate__lte=record_date_lte, record_date__lte=record_date_lte).all()
				if device:
					serializer = SubscriptionSerializer(device, many=True)
					return JsonResponse({'message':'Device Registered from '+request_from_date+', to '+request_to_date+'.', 'devices':serializer.data, 'status_code':200, 'status':True, 'count':len(device)}, status=200)
				return JsonResponse({'message':'No device registered from '+request_from_date+', to '+request_to_date+'.', 'status_code':404, 'status':False}, status=404)
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Error During counting device registered, please try agin letter', 'status':False, 'status_code':500}, status=500)
		else:
			last_24_hour = datetime.datetime.now() - datetime.timedelta(1)
			device = Subscription.objects.filter(firstBillingDate__gte=last_24_hour, record_date__gte=last_24_hour).all()
			if device:
				serializer = SubscriptionSerializer(device, many=True)
				return JsonResponse({'message':'Device Registered in last 24 hours', 'devices':serializer.data, 'status_code':200, 'status':True, 'count':len(device)}, status=200)
			return JsonResponse({'message':'No device registered in last 24 hours', 'status_code':404, 'status':False}, status=404)
			
			
class ActiveDeviceView(APIView):
	# permission_classes = (AllowAny,)

	def post(self, request):
		from itertools import chain
		request_from_date = request.data.get('from', None)
		request_to_date = request.data.get('to', None)

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')

			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				device = FriMarkers.objects.filter(record_date__gte=record_date_gte, record_date__lte=record_date_lte).values('imei').distinct()
				gl_device = GLFriMarkers.objects.filter(record_date__gte=record_date_gte, record_date__lte=record_date_lte).values('imei').distinct()
				
				serializer = FriMarkersCount(device, many=True)
				gl_serializer = GLFriMarkersCount(gl_device, many=True)

				result_list = list(chain(device, gl_device))
				return JsonResponse({'message':'Active Device, from '+request_from_date+', to '+request_to_date+'.', 'devices':serializer.data+gl_serializer.data, 'count':len(result_list), 'status':True, 'status_code':200}, status=200)
				
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Error during retreiving active device, please try again letter', 'status':False, 'status_code':500}, status=500)
		else:
			last_24_hour = datetime.datetime.now() - datetime.timedelta(1)
			device = FriMarkers.objects.filter(record_date__gte=last_24_hour).values('imei').distinct()
			gl_device = GLFriMarkers.objects.filter(record_date__gte=last_24_hour).values('imei').distinct()
			gl_serializer = GLFriMarkersCount(gl_device, many=True)
			
			serializer = FriMarkersCount(device, many=True)
			return JsonResponse({'message':'Device Active in last 24 hours', 'devices':serializer.data+gl_serializer.data, 'status_code':200, 'status':True, 'count':len(device)+len(gl_device)}, status=200)
			# return JsonResponse({'message':'No device active in last 24 hours', 'status_code':200, 'status':False}, status=200)

# categories = SimMapping.objects.filter(category=category).values('model').distinct()

class SubscriptionCanceledCountView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		request_from_date = request.data.get('from', None)
		request_to_date = request.data.get('to', None)

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')

			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				device = WebhookSubscription.objects.filter(kind='subscription_canceled', record_date__gte=record_date_gte, record_date__lte=record_date_lte).values('subscription_id').distinct()
				
				if device:
					device_list = [i['subscription_id'] for i in device]
					subscription = Subscription.objects.filter(subscription_id__in=device_list).all()
					serializer = SubscriptionSerializer(subscription, many=True)
					return JsonResponse({'message':'Subscription Cancelled, from '+request_from_date+', to '+request_to_date+'.', 'devices':serializer.data, 'count':len(subscription), 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'Nosubscription cancelled from '+request_from_date+', to '+request_to_date+'.', 'status_code':200, 'status':False}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Error during retreiving, subscription cancelled . Please try again letter', 'status':False, 'status_code':500}, status=500)
		else:
			last_24_hour = datetime.datetime.now() - datetime.timedelta(1)
			device = WebhookSubscription.objects.filter(record_date__gte=last_24_hour, kind='subscription_canceled').values('subscription_id').distinct()
			if device:
				subscription = Subscription.objects.filter(subscription_id__in=device).all()
				serializer = SubscriptionSerializer(subscription, many=True)
				return JsonResponse({'message':'Subscription Cancelled in last 24 hours', 'devices':serializer.data, 'status_code':200, 'status':True, 'count':len(subscription)}, status=200)
			return JsonResponse({'message':'No subscription cancelled in last 24 hours', 'status':False, 'status_code':200, 'count':0})


class TotalActiveDevice(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		subscription = Subscription.objects.filter(device_in_use=True, is_active=True).count()
		return JsonResponse({'message':'Total active device', 'status_code':200, 'status':True, 'count':subscription}, status=200)



class ReactivatedDeviceView(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		request_from_date = request.data.get('from', None)
		request_to_date = request.data.get('to', None)

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')

			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				subscriptions = WebhookSubscription.objects.filter(kind='subscription_charged_successfully', record_date__gte=record_date_gte, record_date__lte=record_date_lte).values('subscription_id').distinct()
				if subscriptions:
					subscription_instance = Subscription.objects.filter(subscription_id__in=subscriptions).all()
					activated_devices = self.get_activated_device_date_range(record_date_lte, record_date_gte)
					
					res = [i for i in subscription_instance if i not in activated_devices]
					serializer = SubscriptionSerializer(res, many=True)
					return JsonResponse({'message':'Reactivated Device, from : '+request_from_date+', to : '+request_to_date+'.', 'status':True, 'status_code':200, 'devices':serializer.data, 'count':len(res)}, status=200)
				return JsonResponse({'message':'Reactivated Device, from : '+request_from_date+', to : '+request_to_date+'.', 'status':True, 'status_code':200, 'devices':[], 'count':0}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Error during retreiving, Reactivated Device . Please try again letter', 'status':False, 'status_code':500}, status=500)
		else:
			last_24_hour = datetime.datetime.now() - datetime.timedelta(1)
			subscriptions = WebhookSubscription.objects.filter(record_date__gte=last_24_hour, kind='subscription_charged_successfully').values('subscription_id').distinct()
			if subscriptions:
				subscription_instance = Subscription.objects.filter(subscription_id__in=subscriptions, record_date__gte=last_24_hour).all()
				activated_devices = self.get_activated_device_last_24hr(last_24_hour)
				res = [i for i in subscription_instance if i not in activated_devices]

				serializer = SubscriptionSerializer(res, many=True)
				return JsonResponse({'message':'Reactivated device in last 24 hours', 'status':True, 'status_code':200, 'devices':serializer.data, 'count':len(res)}, status=200)
			return JsonResponse({'message':'Reactivated device in last 24 hours', 'status':True, 'status_code':200, 'devices':[], 'count':0}, status=200)


	def get_activated_device_last_24hr(self, date):
		device = Subscription.objects.filter(firstBillingDate__gte=date, record_date__gte=date).all()
		return device


	def get_activated_device_date_range(self, date_lte, date_gte):
		device = Subscription.objects.filter(firstBillingDate__gte=date_gte, record_date__gte=date_gte,firstBillingDate__lte=date_lte, record_date__lte=date_lte).all()
		# print(len(device), ']]]]]]]]]]]]]]]]]]]]]]]')
		return device



class SubscriptionCancelledView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		subscription_canceled = SubscriptionCancelation.objects.all().order_by('-record_date')
		serializer = SubscriptionCancelationSerializer(subscription_canceled, many=True)
		return JsonResponse({'message':'List of subscription cancelled', 'status_code':200, 'status':True, 'subscriptions':serializer.data}, status=200)



class ActivatedNotLoggedView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		user = User.objects.filter(last_login=None).all().order_by('-id')
		serializer = SupportUserSerializer(user, many=True)
		return JsonResponse({'message':'Device Activated but not logged into website', 'status':True, 'status_code':200, 'users':serializer.data}, status=200)
		
# from datetime import datetime
from datetime import timedelta

class SubscriptionActiveNotLoggedIn(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		today = datetime.datetime.today()
		one_month_ago = self.monthdelta(today, -1)
		subscription = Subscription.objects.filter(is_active=True, device_in_use=True).values('customer_id').distinct()
		customer_id = [i.get('customer_id', None) for i in subscription]
		users = User.objects.filter(last_login__lte=one_month_ago, customer_id__in=customer_id, subuser=False).all().order_by('-id')
		serializer = SupportUserSerializer(users, many=True)
		return JsonResponse({'message':'Subscribed but not active', 'status_code':200, 'status':True, 'users':serializer.data}, status=200)


	def monthdelta(self, date, delta):
	    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
	    if not m: m = 12
	    d = min(date.day, [31,
	        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
	    return date.replace(day=d,month=m, year=y)


class ActivatedDeviceNotReportingView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.gps_imei = []
		self.obd_imei = []
		self.activated_device = []
		self.non_reported_device =[]
		self.customer_ids = []

	def get(self, request):

		page = request.GET.get('page', 1)

		end = int(page)*50
		start = end-50

		query = request.GET.get('query', None)

		search_in_user = False

		sub_filter = queue(imei_no__icontains=query) | queue(imei_iccid__icontains=query) | queue(subscription_status__icontains=query) | queue(subscription_id__icontains=query) | queue(customer_id__icontains=query)
		user_filter = queue(first_name__icontains=query) | queue(last_name__icontains=query) | queue(email__icontains=query) | queue(customer_id__icontains=query)
		if query:
			subscriptions = Subscription.objects.filter(is_active=True, device_in_use=True).filter(sub_filter).all()
			if not subscriptions:
				search_in_user = True
				subscriptions = Subscription.objects.filter(is_active=True, device_in_use=True).all()
			self.get_gps_devices()
			self.get_obd_devices()
			self.activated_device = [i.imei_no for i in subscriptions]
			self.reported_devices = self.gps_imei+self.obd_imei
			self.non_reported_device = list(set(self.activated_device)-set(self.reported_devices))
			self.get_user_list()

			
			if search_in_user:
				users = User.objects.filter(customer_id__in=self.customer_ids, subuser=False).filter(user_filter).all().order_by('-id')[start:end]
				users_count = User.objects.filter(customer_id__in=self.customer_ids, subuser=False).filter(user_filter).count()
			else:
				users = User.objects.filter(customer_id__in=self.customer_ids, subuser=False).all().order_by('-id')[start:end]
				users_count = User.objects.filter(customer_id__in=self.customer_ids, subuser=False).count()

			serializer = DeviceNotReportedSerializers(users, many=True)
			for i in serializer.data:
				subscriptions = Subscription.objects.filter(imei_no__in=self.non_reported_device, customer_id=i.get('customer_id')).all()
				sub_serializer = SubscriptionSerializer(subscriptions, many=True)
				i['subscriptions'] = sub_serializer.data
			return JsonResponse({'message':'Activated device not reporting', 'status_code':200, 'status':True, 'user_list':serializer.data, 'count':users_count}, status=200)

		subscriptions = Subscription.objects.filter(is_active=True, device_in_use=True).all()
		self.get_gps_devices()
		self.get_obd_devices()
		self.activated_device = [i.imei_no for i in subscriptions]
		self.reported_devices = self.gps_imei+self.obd_imei
		self.non_reported_device = list(set(self.activated_device)-set(self.reported_devices))
		self.get_user_list()

		users = User.objects.filter(customer_id__in=self.customer_ids).all().order_by('-id')[start:end]
		users_count = User.objects.filter(customer_id__in=self.customer_ids).count()
		serializer = DeviceNotReportedSerializers(users, many=True)
		for i in serializer.data:
			subscriptions = Subscription.objects.filter(imei_no__in=self.non_reported_device, customer_id=i.get('customer_id')).all()
			sub_serializer = SubscriptionSerializer(subscriptions, many=True)
			i['subscriptions'] = sub_serializer.data
		return JsonResponse({'message':'Activated device not reporting', 'status_code':200, 'status':True, 'user_list':serializer.data, 'count':users_count}, status=200)


	def get_gps_devices(self):
		gps = GLFriMarkers.objects.values('imei').distinct()
		gps_imei = [i.get('imei', None) for i in gps]
		self.gps_imei = gps_imei

	def get_obd_devices(self):
		obd = ObdMarkers.objects.values('imei').distinct()
		print(obd)
		obd_imei = [i.get('imei', None) for i in obd]
		self.obd_imei = obd_imei

	def get_user_list(self):
		subscriptions = Subscription.objects.filter(imei_no__in=self.non_reported_device).all()
		self.customer_ids = [i.customer_id for i in subscriptions]



class ReplaceImeiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		imei_old = request.data.get('imei_old', None)
		imei_new = request.data.get('imei_new', None)
		merge_data = request.data.get('merge_data', None)

		if imei_old and imei_new:
			if imei_old == imei_new:
				return JsonResponse({'message':'IMEI Replace Successfully', 'status':True, 'status_code':200}, status=200)
			sim_deactivate_immeidiate_request(imei_old)
			sim_activate_status = sim_activate_immeidiate_request(imei_new)
			if sim_activate_status:
				self.duplicate_subscription(imei_old, imei_new)
				self.update_setting(imei_old, imei_new)
				if merge_data:
					self.replace_imei(imei_old, imei_new)
				return JsonResponse({'message':'IMEI replaced successfully', 'status_code':200, 'status':False}, status=200)
			return JsonResponse({'message':'Error During activating new sim', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'New and old IMEI required', 'status_code':200, 'status':False}, status=400)


	def replace_imei(self, old_imei, new_imei):
		user_trips = UserTrip.objects.filter(imei=old_imei).update(imei=new_imei)
		trip_events = TripEvents.objects.filter(imei=old_imei).update(imei=new_imei)
		voltage = VoltageModel.objects.filter(imei=old_imei).update(imei=new_imei)
		harsh = HarshBehaviourEvent.objects.filter(imei=old_imei).update(imei=new_imei)
		buffer_record = BufferRecord.objects.filter(imei=old_imei).update(imei=new_imei)
		buffer_record_gl = GlBufferRecord.objects.filter(imei=old_imei).update(imei=new_imei)
		trip_cal = TripCalculationData.objects.filter(imei=old_imei).update(imei=new_imei)
		user_trip = UserTrip.objects.filter(imei=old_imei).update(imei=new_imei)
		trip_calculation_gl = TripCalculationGLData.objects.filter(imei=old_imei).update(imei=new_imei)
		reports = Reports.objects.filter(imei=old_imei).update(imei=new_imei)
		zone_notification = ZoneNotificationChecker.objects.filter(imei=old_imei).update(imei=new_imei)
		notification = Notifications.objects.filter(imei=old_imei).update(imei=new_imei)
		sms_log = SmsLog.objects.filter(imei=old_imei).update(imei=new_imei)
		individual_tracking = IndividualTracking.objects.filter(imei=old_imei).update(imei=new_imei)
		pass


	def duplicate_subscription(self, imei_old, imei_new):
		subscription = Subscription.objects.filter(imei_no=imei_old, device_in_use=True, is_active=True).last()
		if subscription:
			serializer = SubscriptionSerializer(subscription)
			sub_data = serializer.data
			sub_data['imei_no'] = imei_new
			sub_data['sim_status'] = True
			new_serializer = SubscriptionSerializer(data=sub_data)
			if new_serializer.is_valid():
				new_serializer.save()
				subscription.sim_status = False
				subscription.is_active = False
				subscription.device_in_use = False
				subscription.save()
				return True
			return False
		return False


	def update_setting(self, imei_old, imei_new):
		old_setting = SettingsModel.objects.filter(imei=imei_old).last()
		new_setting = SettingsModel.objects.filter(imei=imei_new).last()
		settings_data = SettingsSerializer(old_setting).data
		settings_data['imei'] = imei_new
		serializer = SettingsSerializer(new_setting, data=settings_data)
		if serializer.is_valid():
			serializer.save()
		else:
			print(serializer.errors)


class UpdateUsernameView(APIView):
	def post(self, request):
		customer_id = request.data.get('customer_id', None)
		username = request.data.get('username', None)

		user_name = User.objects.filter(username=username).first()
		email_user = User.objects.filter(email=username).first()
		if not user_name and not email_user:
			if customer_id and username:
				user = User.objects.filter(customer_id=customer_id).first()
				if user:
					user.username = username
					user.save()
					return JsonResponse({'message':'Username Updated successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'User not Found, Invalid Customer ID', 'status':False, 'status_code':400}, status_code=400)
			return JsonResponse({'message':'Invalid Request, Customer ID and Username Required', 'status_code':400, 'status':False}, status=400)
		return JsonResponse({'message':'username Already Taken, please try with other username', 'status_code':400, 'status':False}, status=400)


class UserSupportApiView(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		imei = request.data.get('imei', None)
		customer_id = request.data.get('customer_id', None)
		message = request.data.get('message', None)
		category = request.data.get('category', None)

		if customer_id:
			category = self.get_category(imei)
			serializer = EnquiryDetailsSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				loop = asyncio.new_event_loop()
				loop.run_in_executor(None, enquiry_mail, [customer_id, imei, message, category])
				return JsonResponse({'message':'Enquiry Mail Sent Successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid Data', 'status':False, 'status_code':400, 'error':serializer.errors}, status=200)
		return JsonResponse({'message':'Invalid Request Customer ID Required', 'status':False, 'status_code':200}, status=200)

	def get_category(self, imei):
		sim = SimMapping.objects.filter(imei=imei).last()
		if sim:
			if sim.category:
				return sim.category
			else:
				return 'gps'
		return 'gps'



class ManualReviewView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id):
		user = User.objects.filter(customer_id=customer_id).first()
		if user:
			review_mail([user.emailing_address, customer_id, user.first_name, user.last_name])
			# review_mail(['mayur.patil1211@gmail.com', customer_id])
			return JsonResponse({'message':'Review Mail Sent Successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Invalid User', 'status':False, 'status_code':404}, status=404)




class ReplaceReturnedDeviceView(APIView):
	permission_classes = (AllowAny,)
	def __init__(self):
		self.user = None
		self.subscription_instance = None
		self.request_data = None

	def post(self, request, customer_id):
		host = request.META['HTTP_HOST']
		if request.data:
			old_imei = request.data.get('old_imei', None)
			old_iccid = request.data.get('old_iccid', None)
			new_imei = request.data.get('new_imei', None)
			if old_imei and old_iccid and new_imei:
				if Subscription.objects.filter(imei_no=new_imei, device_in_use=True).last():
					return JsonResponse({'message':'IMEI already in use', 'status':False, 'status_code':400}, status=400)
					
				new_sim_instance = SimMapping.objects.filter(imei=new_imei).last()

				if new_sim_instance:
					self.subscription_instance = subscription_instance = Subscription.objects.filter(imei_no=old_imei, device_in_use=True).last()

					if self.subscription_instance:
						self.customer_id = self.subscription_instance.customer_id
						self.subscription_instance.imei_no = new_imei
						self.subscription_instance.imei_iccid = new_sim_instance.iccid
						self.subscription_instance.save()

						self.update_setting(old_imei, self.customer_id, new_imei)
						
						sim_activate_immeidiate_request(new_imei)
						sim_deactivate_immeidiate_request(old_imei)
						
						return JsonResponse({'message':'Device Replaced Successfully', 'status':True, 'status_code':200}, status=200)
					return JsonResponse({'message':'Invalid old IMEI', 'status':False, 'status_code':400}, status=400)
				return JsonResponse({'message':'Invalid New IMEI', 'status':False, 'status_code':404}, status=404)
			return JsonResponse({'message':'Required IMEI, Bad Request', 'status':False, 'status_code':400}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)

	def update_setting(self, imei, customer_id, new_imei):
		print('updating setting')
		setting_update = SettingsModel.objects.filter(imei=str(imei), customer_id=str(customer_id)).last()
		# print('setting_update', setting_update)
		if setting_update:
			setting_update.imei = new_imei
			setting_update.save()
			# setting_update.delete()
		pass



class DeleteReports(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		date1 = datetime.datetime.now() - datetime.timedelta(days=2)
		record_date_lte = datetime.datetime.strptime(str(date1.year)+'-'+str(date1.month)+'-'+str(date1.day)+" 23:59:59", "%Y-%m-%d %H:%M:%S")
		notifications = Reports.objects.filter(record_date_timezone__lte=record_date_lte).all()
		if notifications:
			notifications.delete()
			return JsonResponse({'message':'Reports Deleted Successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'No Reports Found', 'status':True, 'status_code':200}, status=200)


class DeleteZoneReports(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		date1 = datetime.datetime.now() - datetime.timedelta(days=2)
		record_date_lte = datetime.datetime.strptime(str(date1.year)+'-'+str(date1.month)+'-'+str(date1.day)+" 23:59:59", "%Y-%m-%d %H:%M:%S")
		notifications = ZoneNotificationChecker.objects.filter(report_time__lte=record_date_lte).all()
		if notifications:
			notifications.delete()
			return JsonResponse({'message':'Reports Deleted Successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'No Reports Found', 'status':True, 'status_code':200}, status=200)



class TripsGeneratedCount(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		date = request.GET.get('date', None)
		date = date.split('-')

		from_date = str(date[2])+'-'+str(date[1])+'-'+str(date[0])+' 00:00:00'
		to_date = str(date[2])+'-'+str(date[1])+'-'+str(date[0])+' 23:59:59'
		user_trips = UserTrip.objects.filter(record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).count()
		print(user_trips)
		return JsonResponse({'message':'User Trips for date '+request.GET.get('date', None), 'status':True, 'status_code':200}, status=200)



class UpdateSubscriptionIdApiView(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		imei = request.data.get('imei', None)
		customer_id = request.data.get('customer_id', None)
		subscription_id = request.data.get('subscription_id', None)

		subscription = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()
		if subscription:
			subscription.subscription_id = subscription_id
			subscription.save()
			return JsonResponse({'message':'Subscription ID updated Successfully', 'status':True, 'status_code':True}, status=200)
		return JsonResponse({'message':'Invalid IMEI or Customer ID', 'status_code':404, 'status':False}, status=404)


class ImeiCommandsSavedApiView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		device_commands = DeviceCommands.objects.all()
		serializer = DeviceCommandsSerializer(device_commands, many=True)
		return JsonResponse({'message':'IMEI command List', 'status':True, 'status_code':200, 'imei_commands':serializer.data}, status=200)


	def delete(self, request):
		id = request.data.get('id', None)
		if id:
			device_command = DeviceCommands.objects.filter(id=id).last()
			print(device_command)
			if device_command:
				device_command.delete()
		return JsonResponse({'message':'Command Deleted Successfully', 'status':True, 'status_code':200}, status=200)

	def post(self, request):
		imei = request.data.get('imei', None)
		if request.data.get('imei', None) and request.data.get('command', None):
			request.data.get('command', None).replace('imei', imei)
			serializer = DeviceCommandsSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return JsonResponse({'message':'Command Saved from IMEI '+imei, 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Error During Insert Command', 'status':False, 'status_code':400, 'error':serializer.errors}, status=400)
		return JsonResponse({'message':'IMEI and Command Required', 'status':True, 'status_code':200}, status=200)



class CommandListApiView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		commands = DeviceCommandsList.objects.all()
		serializer = DeviceCommandsListSerializers(commands, many=True)
		return JsonResponse({'message':'Device Commands', 'status':True, 'status_code':200, 'commands':serializer.data}, status=200)


class RemoveDeviceInUseView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei):
		subscription = Subscription.objects.filter(imei_no=imei, customer_id=customer_id).last()
		if subscription:
			subscription.device_in_use = False
			subscription.save()
			return JsonResponse({'message':'Device In Use Deactivated', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Invalid Device', 'status':False, 'status_code':400}, status=200)


class SendMailApiView(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		subject = request.data.get('subject', None)
		email = request.data.get('email', None)
		content = request.data.get('content', None)

		if email and subject and content:
			send_mail_from_support(email, subject, content)
			return JsonResponse({'message':'Email Sent Successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Fields Required : Email, Subject and Content', 'status':False, 'status_code':400}, status=400)


class SendBatchMessages(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		subject = request.data.get('subject', None)
		content = request.data.get('content', None)
		if subject and content:
			try:
				send_batch_message(subject, content)
			except(Exception)as e:
				return JsonResponse({'message':'Error During Sending Mail', 'status':False, 'status_code':400, 'error':str(e)}, status=400)
			return JsonResponse({'message':'Sent Email Successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Fields Required : Subject and Content', 'status':False, 'status_code':400}, status=400)



class FeedbackListApi(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		page = request.GET.get('page', 1)

		end = int(page)*50
		start = end-50

		query = request.GET.get('query', None)

		if query:
			_filter = queue(first_name__icontains=query) | queue(last_name__icontains=query) | queue(email__icontains=query)
			feed_back = FeedBackModel.objects.filter(_filter).order_by('-record_date')[start:end]
			feed_back_count = FeedBackModel.objects.filter(_filter).order_by('-record_date').count()
			serializer = FeedbackSupportList(feed_back, many=True)
			return JsonResponse({'message':'List of user', 'status':True, 'status_code':200, 'customers':serializer.data, 'total_user':feed_back_count}, status=200)

		
		feed_back = FeedBackModel.objects.all().order_by('-record_date')[start:end]
		feed_back_count = FeedBackModel.objects.all().order_by('-record_date').count()
		serializer = FeedbackSupportList(feed_back, many=True)
		return JsonResponse({'message':'List of user', 'status':True, 'status_code':200, 'customers':serializer.data, 'total_user':feed_back_count}, status=200)

class MarkAmzonReviewApi(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, email):
		if email:
			feed_back = FeedBackModel.objects.filter(email=email).last()
			if feed_back:
				feed_back.amazon_feedback = True
				feed_back.save()
				return JsonResponse({'message':'Mark as gave feedback on amazon', 'status':True, 'status_code':True}, status=200)
			return JsonResponse({'message':'This email has no record', 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'Email Required', 'status':False, 'status_code':400}, status=200)