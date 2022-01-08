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

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q as queue
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from app.events import main_location_machine

import string
import random
import datetime
from datetime import timedelta
import time

from app.serializers import *
from app.models import *


from listener.models import * 
from listener.serializers import *

from services.sim_update_service import *
from services.mail_sender import *
from services.models import *
from services.helper import *
from services.serializers import *


exclude_obd = [None, 0, 0.0]
time_fmt = '%Y-%m-%d %H:%M:%S'




class SimDignosticsApiView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		sim_iccid = SimMapping.objects.filter(imei=imei).first()
		if sim_iccid:
			if sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod' or sim_iccid.provider == 'pod_att':
				token, accountId = get_pod_token()
				dignostics = self.get_dignostics(token, sim_iccid.iccid, accountId)
				return JsonResponse({'message':'Sim Dignostics', 'status':True, 'status_code':200, 'dignostics':dignostics}, status=200)
			return JsonResponse({'message':'Sim Dignostics', 'status':True, 'status_code':201, 'dignostics':{}}, status=200)
		return JsonResponse({'message':'Invalid IMEI', 'status':False, 'status_code':400}, status=400)


	def get_dignostics(self, token, sim_iccid, accountId):
		url = "https://api.podiotsuite.com/v3/assets/{}/diagnostic?accountId={}".format(str(sim_iccid), accountId)
		payload = {}
		headers = {
		    'x-access-token': token
		    }

		response = requests.request("GET", url, headers=headers, data = payload)
		return response.json()

# curl -X GET "https://api.podiotsuite.com/v3/assets/8944501005190286751/diagnostic?accountId=6faa5709-d8b5-4760-b30b-0f1586416596" 
# -H "accept: application/json" -H "x-access-token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI1Y2ZmOGZlYmM3MjBiOTAwMTI2MjdhNGMifQ.NB0urq_RKI2djZyxEDyav4wUwp8cXiKLkM4e_ldMOWI"



class SimLocationApiView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		sim_iccid = SimMapping.objects.filter(imei=imei).first()
		if sim_iccid:
			token, accountId = get_pod_token()
			dignostics = self.get_location(token, sim_iccid.iccid, accountId)
			return JsonResponse({'message':'Sim Location', 'status':True, 'status_code':200, 'location':dignostics}, status=200)

		return JsonResponse({'message':'Invalid IMEI', 'status':False, 'status_code':400}, status=400)


	def get_location(self, token, sim_iccid, accountId):
		url = "https://api.podiotsuite.com/v3/assets/{}/location?accountId={}".format(str(sim_iccid), accountId)
		payload = {}
		headers = {
		    'x-access-token': token
		    }

		response = requests.request("GET", url, headers=headers, data = payload)
		return response.json()