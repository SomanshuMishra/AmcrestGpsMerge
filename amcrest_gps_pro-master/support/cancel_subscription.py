from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate

from django.template.loader import render_to_string

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import datetime
import asyncio
import base64
import hashlib

from user.models import *
from user.serializers import *

from app.serializers import *
from app.models import *

from services.models import *
from services.serializers import *
from services.sim_update_service import *
from services.helper import *
from services.mail_sender import *

import braintree

from django.template.loader import render_to_string


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

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


from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def get_user(user_id):

    user = User.objects.filter(id=user_id).first()
    serializer = UserSerialzer(user)
    return serializer.data


def get_subscription_details(customer_id):
    subscription_instance = Subscription.objects.filter(customer_id=customer_id).all()
    serializer = SubscriptionSerializer(subscription_instance, many=True)
    return serializer.data


class SubscriptionCancelationView(APIView):
    permission_classes = (AllowAny,)

    def __init__(self):
        self.user = None
        self.subscription_instance = None
        self.request_data = None

    def post(self, request):
        customer_id = request.data.get('customer_id', None)
        imei = request.data.get('imei', None)
        self.request_data = request.data
        close_old_connections()
        if customer_id:
            self.user = user = User.objects.filter(customer_id=customer_id, subuser=False).first()
            if user:
                self.subscription_instance = subscription_instance = Subscription.objects.filter(imei_no=imei, customer_id=user.customer_id, device_in_use=True).last()
                if subscription_instance:
                    if self.cancel_subscription(subscription_instance.subscription_id):
                        return JsonResponse({'message':'Subscription Cancelled', 'status':True, 'status_code':200}, status=200)
                    return JsonResponse({'message':'Error during cancelling subscription.', 'status':False, 'status_code':400}, status=400)
                return JsonResponse({'message':'Invalid Customer ID or IMEI', 'status':False, 'status_code':404}, status=404)
            return JsonResponse({'message':'invalid user, please provide valid customer id', 'status':False, 'status_code':404}, status=404)
        return JsonResponse({'message':'Customer ID Required, Bad Request', 'status':False, 'status_code':400}, status=400)


    def cancel_subscription(self, subscription_id):
        try:
            result = gateway.subscription.cancel(subscription_id)
            if result.is_success:
                return True
        except(Exception)as e:
            pass
        return False

    def prepare_details(self):
        if self.user:
            serializer = UserSerialzer(self.user)
            return serializer.data
        return {}


