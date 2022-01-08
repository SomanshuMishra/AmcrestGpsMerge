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
import base64
import hashlib

from .serializers import *
from .models import *

from app.models import *
from app.serializers import *

from user.models import *
from user.serializers import *

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



class ServerStatusApiView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		return JsonResponse({'message':'Server Running', 'status':True, 'status_code':200}, status=200)


class TimeZoneView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		time_zones = TimeZoneModel.objects.all()
		close_old_connections()
		serializer = TimeZonesSerializer(time_zones, many=True)
		return JsonResponse({'message':'Time Zone List', 'status':True, 'status_code':200, 'time_zone':serializer.data}, status=200)


class CountriesView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		countries = Countries.objects.all()
		close_old_connections()
		serializer = CountriesSerializer(countries, many=True)
		return JsonResponse({'message':'Country List', 'status':True, 'status_code':200, 'countries':serializer.data}, status=200)


class StatesView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, country_id):
		states = States.objects.filter(country = country_id).all()
		close_old_connections()
		serializer = StatesSerializer(states, many=True)
		return JsonResponse({'message':'States List', 'status':True, 'status_code':200, 'states':serializer.data}, status=200)


class LangaugesView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        langauges = Langauges.objects.all()
        close_old_connections()
        serializer = LangaugeSerializer(langauges, many=True)
        return JsonResponse({'message':'List of Langauges', 'status':True, 'status_code':200, 'langauges':serializer.data}, status=200)


class ImeiValidationView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, imei):
		sim_mapping = SimMapping.objects.filter(imei=imei).first()
		subscription = Subscription.objects.filter(imei_no=imei, is_active=True).last()
		close_old_connections()
		if not sim_mapping:
			return JsonResponse({'message':'Invalid IMEI, please try with valid IMEI', 'status':False, 'status_code':404}, status=404)
		if subscription:
			return JsonResponse({'message':'IMEI alredy in use, please try with another IMEI', 'status':False, 'status_code':200}, status=200)
		serializer = SimMappingSerializer(sim_mapping)
		return JsonResponse({'message':'Valid IMEI', 'status':True, 'status_code':200, 'details':serializer.data}, status=200)


class SimMappingApiView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		imei = request.GET.get('imei', None)
		if imei:
			sim_mapping = SimMapping.objects.filter(imei=imei).first()
			if sim_mapping:
				serializer = SimMappingSerializer(sim_mapping)
				return JsonResponse({'message':'Found IMEI', 'status':True, 'status_code':200, 'sim_mapping':serializer.data}, status=200)
			return JsonResponse({'message':'No matching IMEI', 'status':False, 'status_code':404}, status=404)
		return JsonResponse({'message':'Bad Request, IMEI Required', 'status':False, 'status_code':400}, status=200)

	def post(self, request):
		if request.data:
			serializer = SimMappingSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return JsonResponse({'message':'IMEI Saved successfully', 'status':True, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid Data, Please Provide Valid Data', 'status':False, 'status_code':200, 'error':serializer.errors}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':200}, status=200)


class ServicePlanView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		service_plan = ServicePlan.objects.all().order_by('price')
		close_old_connections()
		serializer = ServicePlanSerializer(service_plan, many=True)
		return JsonResponse({'message':'Service Plan list', 'status':True, 'status_code':200, 'plans':serializer.data}, status=200)


class ServicePlanObdView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		service_plan = ServicePlanObd.objects.all().order_by('price')
		close_old_connections()
		serializer = ServicePlanObdSerializer(service_plan, many=True)
		return JsonResponse({'message':'Service Plan list', 'status':True, 'status_code':200, 'plans':serializer.data}, status=200)


class AllServicePlan(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		service_plan = ServicePlan.objects.all()
		close_old_connections()
		serializer = ServicePlanSerializer(service_plan, many=True)

		service_plan_obd = ServicePlanObd.objects.all()
		close_old_connections()
		serializer_obd = ServicePlanObdSerializer(service_plan, many=True)
		return JsonResponse({'message':'All Service Plan list', 'status':True, 'status_code':200, 'plans':serializer.data+serializer_obd.data}, status=200)


class CombinePlanList(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		service_plan = ServicePlan.objects.all()
		serializer = ServicePlanSerializer(service_plan, many=True)
		service_plan = ServicePlanObd.objects.all()
		serializer_obd = ServicePlanObdSerializer(service_plan, many=True)
		return JsonResponse({'message':'Service Plan list', 'status':True, 'status_code':200, 'plans':serializer.data+serializer_obd.data}, status=200)


class CancelSubscriptionValidation(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, imei):
		subscription = Subscription.objects.filter(imei_no=imei, is_active=True).last()
		close_old_connections()
		if subscription:
			return JsonResponse({'message':'IMEI Deactivation proess Validation', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'IMEI Deactivation proess Validation', 'status':False, 'status_code':404}, status=404)


class CardValidateView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id, card_number):
		response = {}
		client_token = gateway.customer.find(customer_id)
		if client_token.credit_cards[0].bin == card_number:
			response['first_name'] = client_token.credit_cards[0].billing_address.first_name
			response['last_name'] = client_token.credit_cards[0].billing_address.last_name
			response['last4'] = client_token.credit_cards[0].last_4
			response['billing_address'] = client_token.credit_cards[0].billing_address.street_address
			return JsonResponse({'message':'Valid Number', 'status':True, 'status_code':200, 'response':response}, status=200)
		return JsonResponse({'message':'Invalid Number', 'status':False, 'status_code':400}, status=200)


class DeviceModelView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		device_models = DeviceModel.objects.all()
		serializer = DeviceModelSerializer(device_models, many=True)
		return JsonResponse({'message':'Device Model Name', 'status_code':200, 'status':True, 'device_model':serializer.data})


class UserImeiList(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id):
		# subscription = Subscription.objects.filter(customer_id=customer_id).order_by('imei_no').values('imei_no','nextBillingDate', 'activated_plan_id', 'activated_plan_description').distinct()
		subscription = Subscription.objects.filter(customer_id=customer_id, is_active=True, device_in_use=True).all()
		close_old_connections()
		serializer = ImeiListSerializer(subscription, many=True)
		return JsonResponse({'message':'Imei List', 'status_code':200, 'status':True, 'devices':serializer.data}, status=200)


class CheckEmailExist(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, email):
		user = User.objects.filter(email=email).first()
		if user:
			return JsonResponse({'message':'User Already Exist', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'User not exist', 'status':False, 'status_code':400}, status=200)


class DeviceFrequencyView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		device_frequency = DeviceFrequency.objects.all().order_by('device_frequency')
		close_old_connections()
		serializer = DeviceFrequencySerializer(device_frequency, many=True)
		return JsonResponse({'message':'Device Frequency List', 'status':True, 'status_code':200, 'device_frequency':serializer.data}, status=200)


class DeviceFrequencyObdView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		device_frequency = DeviceFrequencyObd.objects.all().order_by('device_frequency')
		close_old_connections()
		serializer = DeviceFrequencyObdSerializer(device_frequency, many=True)
		return JsonResponse({'message':'Device Frequency List', 'status':True, 'status_code':200, 'device_frequency':serializer.data}, status=200)

import togeojsontiles

class GpxToJsonView(APIView):
	# permission_classes = (AllowAny,)
	parser_classes = (MultiPartParser,JSONParser,)
	def post(self, request):
		file = request.FILES.get('file', None)
		if file:
			togeojsontiles.gpx_to_geojson(file_gpx='sample.gpx', file_geojson='test.geojson')
			return JsonResponse({'message':'GPX file geojson successfull', 'status':False, 'status_code':200}, status=200)
		return JsonResponse({'message':'Bad request', 'status':False, 'status_code':400}, status=200)


class NoticeView(APIView):
	def get(self, request):
		app_conf = AppConfiguration.objects.filter(key_name='notice').first()
		if app_conf:
			return JsonResponse({'message':'Notice', 'status':True, 'status_code':200, 'notice':app_conf.key_value})
		return JsonResponse({'message':'Notice', 'status':True, 'status_code':200, 'notice':[]})


class DealerInfo(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, customer_id):
		if customer_id and not customer_id == 'undefined':
			user = User.objects.filter(customer_id=customer_id, is_dealer=True, subuser=False).last()
			if user:
				serializer = UserSerialzer(user)
				return JsonResponse({'message':'Dealer Valid', 'status_code':200, 'status':True, 'email':user.email, 'user_details':serializer.data}, status=200)
			return JsonResponse({'message':'Invalid Dealer', 'status_code':400, 'status':False}, status=400)
		return JsonResponse({'message':'Invalid Customer ID', 'status':False, 'status_code':400}, status=400)



class MobileServiceProviderView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		mobile_service = MobileServiceProvider.objects.all().order_by('mobile_provider_name')
		serializer = MobileServiceProviderSerializer(mobile_service, many=True)
		return JsonResponse({'message':'Mobile Service Provider', 'status':True, 'status_code':200, 'providers':serializer.data}, status=200)


class LocationConstant(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		const = AppConfiguration.objects.filter(key_name='location_constant').last()
		if const:
			result = hashlib.md5(const.key_value.encode())
			result = result.hexdigest()
			return JsonResponse({'message':'Location Constant', 'status':True, 'status_code':200, 'location':result}, status=200)
		return JsonResponse({'message':'Location Constant', 'status':True, 'status_code':400, 'location':None}, status=200)


class AppVersionView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		app_version = AppVersion.objects.first()
		serializer = AppVersionSerializer(app_version)
		return JsonResponse({'message':'App Version Info', 'status':True, 'status_code':200, 'app_version':serializer.data}, status=200)



class FrequencyListForImei(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, imei):
		category = request.GET.get('category', 'gps')
		if category:
			if category == 'gps':
				subscription = Subscription.objects.filter(imei_no=imei).last()
				if subscription:
					service_plan = ServicePlan.objects.filter(service_plan_id=subscription.activated_plan_id).last()
					if service_plan:
						base_plan = DeviceFrequency.objects.filter(device_frequency_key=service_plan.base_device_frequency).last()
						if base_plan:
							plans_to_send = DeviceFrequency.objects.filter(device_frequency__gte=base_plan.device_frequency).all()
							serializer = DeviceFrequencySerializer(plans_to_send, many=True)
							return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data}, status=200)
						else:
							plans_to_send = DeviceFrequency.objects.filter(device_frequency__gte=1).all()
							serializer = DeviceFrequencySerializer(plans_to_send, many=True)
							return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data, 'error':'No Base Plan'}, status=200)
					else:
						plans_to_send = DeviceFrequency.objects.filter(device_frequency__gte=1).all()
						serializer = DeviceFrequencySerializer(plans_to_send, many=True)
						return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data, 'error':'No Service Plan'}, status=200)
				else:
					plans_to_send = DeviceFrequency.objects.filter(device_frequency__gte=1).all()
					serializer = DeviceFrequencySerializer(plans_to_send, many=True)
					return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data, 'error':'No Subscription'}, status=200)
			elif category == 'obd':
				subscription = Subscription.objects.filter(imei_no=imei).last()
				if subscription:
					service_plan = ServicePlanObd.objects.filter(service_plan_id=subscription.activated_plan_id).last()
					if service_plan:
						base_plan = DeviceFrequencyObd.objects.filter(device_frequency_key=service_plan.base_device_frequency).last()
						if base_plan:
							plans_to_send = DeviceFrequencyObd.objects.filter(device_frequency__gte=base_plan.device_frequency).all()
							serializer = DeviceFrequencyObdSerializer(plans_to_send, many=True)
							return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data}, status=200)
						else:
							plans_to_send = DeviceFrequencyObd.objects.filter(device_frequency__gte=1).all()
							serializer = DeviceFrequencyObdSerializer(plans_to_send, many=True)
							return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data, 'error':'No Base Plan'}, status=200)
					else:
						plans_to_send = DeviceFrequencyObd.objects.filter(device_frequency__gte=1).all()
						serializer = DeviceFrequencyObdSerializer(plans_to_send, many=True)
						return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data, 'error':'No Service Plan'}, status=200)
				else:
					plans_to_send = DeviceFrequencyObd.objects.filter(device_frequency__gte=1).all()
					serializer = DeviceFrequencyObdSerializer(plans_to_send, many=True)
					return JsonResponse({'message':'Frequency List', 'status':True, 'status_code':200, 'frequency':serializer.data, 'error':'No Subscription'}, status=200)
		return JsonResponse({'message':'Category Required', 'status':False, 'status_code':400}, status=200)

class ImportantNoticeApiView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request):
		category = request.GET.get('category', None)
		app_conf = None
		if category == 'gps':
			app_conf = AppConfiguration.objects.filter(key_name='important_notice_gps').first()
		else:
			app_conf = AppConfiguration.objects.filter(key_name='important_notice_obd').first()
		if app_conf:
			return JsonResponse({'message':'Important Notice', 'status':True, 'status_code':200, 'notice':app_conf.key_value}, status=200)
		return JsonResponse({'message':'Important Notice', 'status':False, 'status_code':200, 'notice':''}, status=200)


class GetCommandApiView(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, imei):
		device_commads = DeviceCommands.objects.filter(imei=imei).first()
		if device_commads:
			return JsonResponse({'message':'Device Command', 'status':True, 'status_code':200, 'command':device_commads.command}, status=200)
		return JsonResponse({'message':'Device Command', 'status':False, 'status_code':200, 'command':None}, status=200)

	def delete(self, request, imei):
		device_commads = DeviceCommands.objects.filter(imei=imei).first()
		if device_commads:
			device_commads.delete()
			return JsonResponse({'message':'Command Deleted', 'status_code':200, 'status':True}, status=200)
		return JsonResponse({'message':'Command Deleted', 'status_code':200, 'status':True}, status=200)



class TestAPI(APIView):
	def get(self, request):
		pass
		return JsonResponse({'message':'Hi', 'status':200, 'status_code':200}, status=200)