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
from app.zone_notification import obd_zone_notification_maker

from user.models import *
from user.serializers import *

from services.sim_update_service import *
from services.mail_sender import *
from services.models import *
from services.helper import *
from services.serializers import *


from support.models import *

from .serializers import *
from .models import *

import braintree
import _thread


class GeoFenceApiView(APIView):
	permission_classes = (AllowAny,)
	def post(self, request):
		serializer = GeoFenceObdSerializer(data=request.data.get('details', None))
		if serializer.is_valid():
			serializer.save()
		else:
			print(serializer.errors)
		_thread.start_new_thread(obd_zone_notification_maker.start_zone_notification, (request.data.get('imei'), request.data.get('details', None)))
		return JsonResponse({'message':'Geo Fence Received Successfully', 'status':True, 'status_code':200}, status=200)