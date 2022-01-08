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

from .serializers import *
from .models import *

from app.models import *
from app.serializers import *

from listener.models import *

from user.models import *

from .sim_update_service import *
from .mail_sender import *

import braintree


class UpdateRecord(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		if request.data.get('imei', None):
			self.update_fri(request.data.get('imei', None))
			self.update_stt(request.data.get('imei', None))
		return JsonResponse({'message':'Record Updated Succssfully', 'status':True, 'status_code':200}, status=200)


	def update_fri(self, imei):
		gl_fri = GLFriMarkers.objects.filter(imei=imei, send_time__gte=20190701181252).all()
		for i in gl_fri:
			if i.longitude>0:
				i.longitude = -i.longitude
				# print(-i.longitude>0)
				i.save()
				# break

	def update_stt(self, imei):
		gl_fri = SttMarkers.objects.filter(imei=imei, send_time__gte=20190701181435).all()
		for i in gl_fri:
			if i.longitude>0:
				i.longitude = -i.longitude
				# print(-i.longitude>0)
				i.save()
				# break
