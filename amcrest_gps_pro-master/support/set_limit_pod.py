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


class SetLimitApiView(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		token, accountId = get_pod_token()
		iccid = request.data.get('iccid', None)
		limit = request.data.get('limit', None)
		sms_limit = request.data.get('sms_limit', None)

		status = self.set_limit(token, accountId, iccid, limit, sms_limit)
		if status:
			return JsonResponse({'message':'Setting limit done successfully', 'status':True, 'status_code':200}, status=200)
		else:
			return JsonResponse({'message':'Error During setting limit to the sim, please check the details you sending', 'status':False, 'status_code':400}, status=400)

	def set_limit(self, token, accountId, iccid, limit, sms_limit):
		url = "https://api.podiotsuite.com/v3/assets/{}/limit".format(str(iccid))
			
		if limit and sms_limit and limit != '' and limit != 'undefined' and sms_limit != '' and sms_limit != 'undefined':
			payload = "{ \"accountId\": \""+accountId+"\", \"datalimit\": \""+str(limit)+"\", \"smslimit\":"+str(sms_limit)+"}"
		elif limit and limit != '' and limit != 'undefined':
			payload = "{ \"accountId\": \""+accountId+"\", \"datalimit\": \""+str(limit)+"\"}"
		elif sms_limit and sms_limit != '' and sms_limit != 'undefined':
			payload = "{ \"accountId\": \""+accountId+"\", \"smslimit\": \""+str(sms_limit)+"\"}"

		else:
			payload = None


		if payload:
			headers = {
			    'Content-Type': "application/json",
			    'x-access-token': token,
			    'Cache-Control': "no-cache"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)

			if str(response.status_code) == "200":
				return True
			else:
				return False
		else:
			return False