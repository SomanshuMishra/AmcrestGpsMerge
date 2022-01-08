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


# class DeleteUserApiView(APIView):
# 	def post(self, request):
# 		customer_id = request.data.get('customer_id', None)
# 		user = User.object.filter(customer_id=customer_id).last()
# 		if user:
# 			subscriptions = Subscription.objects.filter(customer_id=customer_id, is_active=True, device_listing=True).all()
# 			if subscriptions:
# 				self.cancel_subscription(subscriptions)
# 				self.suspend_sim_cards(subscriptions)
# 				self.delete_settings(subscriptions)
# 			user.is_active = False
# 			user.save()
# 			return JsonResponse({'message':'User Deleted Successfully', 'status':True, 'status_code':200}, status=200)
# 		return JsonResponse({'message':'Invalid Customer ID, User not Found', 'status':False, 'status_code':404}, status=404)