from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.contrib.auth.hashers import make_password, check_password

from app.models import *
from app.serializers import *

from user.models import *
from user.serializers import *

from services.models import *

User = get_user_model()

class UserLoader(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			time_zone = request.data.get('time_zone', None)
			request.data['time_zone'] = self.get_timezone(time_zone)
			request.data['time_zone_description'] = time_zone
			request.data['country'] = self.get_country(request.data.get('country', None))
			try:
				serializer = UserWriteSerialzer(data=request.data)
				if serializer.is_valid():
					serializer.save()
				else:
					print(serializer.errors)
					return JsonResponse({'message':'Added to db', 'status':True, 'status_code':200}, status=400)
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Something Wrong Please try agin letter for this record', 'status':False, 'status_code':400}, status=400)
			return JsonResponse({'message':'Added to db', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False}, status=400)


	def get_timezone(self, time_zone_desc):
		if time_zone_desc:
			time_zone = TimeZoneModel.objects.filter(description=time_zone_desc.lstrip().rstrip()).first()
			if time_zone:
				return time_zone.time_zone
		return 'US/Eastern'

	def get_country(self, country_id):
		if country_id:
			country = Countries.objects.filter(id=country_id).first()
			if country:
				return country.country_name
		return 'United States'



class SubscriptionLoader(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			customer_id = request.data.get('customer_id')
			if customer_id:
				user = User.objects.filter(customer_id=customer_id, subuser=False).first()
				if user:
					request.data['gps_id'] = user.id
					serializer = SubscriptionSerializer(data=request.data)
					if serializer.is_valid():
						serializer.save()
					else:
						print(serializer.errors)
						return JsonResponse({'message':'Error during saving subscription', 'status':False, 'status_code':400}, status=400)
					return JsonResponse({'message':'Subscription saved successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'User not found', 'status':False, 'status_code':400}, status=400)
			return JsonResponse({'message':'Customer id required', 'status':False, 'status_code':400}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)


class SettingLoader(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			details = self.get_details(request.data.get('customer_id'))
			request.data['email'] = details.get('email', None)
			request.data['phone'] = details.get('phone', None)
			setting_instance = SettingsModel.objects.filter(imei=request.data.get('imei', None)).first()
			if setting_instance:
				serializer = SettingsSerializer(setting_instance, data=request.data)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({'message':'Settings saved', 'status':True, 'status_code':200}, status=200)
				else:
					print(serializer.errors)
					return JsonResponse({'message':'Unable to update settings', 'status':False, 'status_code':400}, status=400)
			else:
				print(request.data)
				serializer = SettingsSerializer(data=request.data)
				if serializer.is_valid():
					serializer.save()
					return JsonResponse({'message':'Setting saved successfully', 'status':True, 'status_code':200}, status=200)
				print(serializer.errors)
				return JsonResponse({'message':'Unable to save setting', 'status':False, 'status_code':200}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)

	def get_details(self, customer_id):
		user = User.objects.filter(customer_id=customer_id, subuser=False).last()
		if user:
			details = {
				"email":user.email,
				"phone":user.phone_number
			}
			return details
		return {"email":None, "phone":None}



class ReportLoader(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			serializer = ReportsSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
			else:
				print(serializer.errors)
				return JsonResponse({'message':'Invalid Data', 'status':400, 'status_code':False}, status=400)
			return JsonResponse({'message':'Reports saved successfully', 'status':True, 'status_code':200}, status=200)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)


class ZoneLoader(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data:
			zone_alert = request.data.get('zone_alert', None)
			serializer = ZoneWriteSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				if zone_alert:
					for i in zone_alert:
						i['zone'] = serializer.data.get('id')
						i['category'] = 'gps'
						za_serializer = ZoneAlertSerializer(data=i)
						if za_serializer.is_valid():
							za_serializer.save()
						else:
							print(za_serializer.errors)
				return JsonResponse({'message':'Zone saved successfully', 'status':True, 'status_code':200}, status=200)
			print(serializer.errors)
			return JsonResponse({'message':'Zone Not saved, Invalid data', 'status':False, 'status_code':400}, status=400)
		return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)