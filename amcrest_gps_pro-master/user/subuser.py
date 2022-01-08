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


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER




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



class SubuserAddApiView(APIView):
    # permission_classes = (AllowAny,)
    def post(self, request):
        close_old_connections()
        if request.data:
            user_id = request.data.get('user')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            password = request.data.get('password')
            address = request.data.get('address')
            city = request.data.get('city')
            state = request.data.get('state')
            zip = request.data.get('zip')


            if user_id:
                primary_user = User.objects.filter(id=user_id, subuser=False).last()
                if not self.check_limit(primary_user):
                    return JsonResponse({'message':'Subuser limit exceeded, cannot add subuser.', 'status':False, 'status_code':400}, status=200)

                if primary_user:
                    if first_name and last_name and email and password:

                        if self.already_exist(email):
                            return JsonResponse({'message':'User already exist with this email id.', 'status_code':400, 'status':400}, status=200)
                        if address:
                            pass
                        else:
                            address = primary_user.address
                        temp_primary = primary_user
                        user_obj = {
                            'first_name':first_name,
                            'last_name':last_name,
                            'email':email,
                            'password':password,
                            'address':address,
                            'time_zone': temp_primary.time_zone,
                            'customer_id':primary_user.customer_id,
                            'language':primary_user.language,
                            'uom':primary_user.uom,
                            'time_zone_description':temp_primary.time_zone_description,
                            'emailing_address':temp_primary.emailing_address,
                            'mobile_carrier':temp_primary.mobile_carrier,
                            'time_format':temp_primary.time_format,
                            'date_format':temp_primary.date_format,
                            'regenerate_trip':temp_primary.regenerate_trip,
                            'subuser':True,
                            'primary_user':user_id
                        }
                        serializer = UserWriteSerialzer(data=user_obj)
                        if serializer.is_valid():
                            serializer.save()
                            return JsonResponse({'message':'Subuser added successfully', 'status':True, 'status_code':200}, status=200)
                        return JsonResponse({'message':'Invalid data, Error during adding subuser.', 'status':False, 'status_code':400}, status=200)
                    return JsonResponse({'message':'First Name, Last Name, Email ID and Password required.', 'status':False, 'status_code':400}, status=200)
                return JsonResponse({'message':'Invalid User, Not authorized to add user.', 'status':False, 'status_code':400}, status=200)
            return JsonResponse({'message':'Invalid Request, User ID required.', 'status':False, 'status_code':400}, status=200)
        return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200)

    def check_limit(self, user):
        app_conf = AppConfiguration.objects.filter(key_name='subuser_limit').last()
        if app_conf:
            try:
                limit = int(app_conf.key_value)
            except(Exception)as e:
                limit = 2

        else:
            limit = 2

        # print(app_conf.key_value)
        if User.objects.filter(customer_id=user.customer_id, subuser=True).count() >= limit:
            return False
        else:
            return True

    def already_exist(self, email):
        if email:
            if User.objects.filter(email=email).last():
                return True
            else:
                return False
        return False

    def delete(self, request):
        id = request.data.get('subuser_id')
        if id:
            user = User.objects.filter(id=id).last()

            if user:
                if user.subuser:
                    user.delete()
                    return JsonResponse({'message':'Sub user deleted successfully', 'status':True, 'status_code':200}, status=200)
                return JsonResponse({'message':'Requested user delete is not subuser, Cannot delete user.', 'status':False, 'status_code':400}, status=200)
            return JsonResponse({'message':'Invalid user id cannot find user.', 'status':False, 'status_code':400}, status=200)
        return JsonResponse({'message':'User ID required.', 'status':False, 'status_code':400}, status=200)


    def get(self, request):
        customer_id = request.GET.get('customer_id')
        if customer_id:
            user = User.objects.filter(customer_id=customer_id, subuser=True).all()
            serializer =UserSerialzer(user, many=True)
            return JsonResponse({'message':'Subuser List', 'status':True, 'status_code':200, 'subusers':serializer.data}, status=200)
        return JsonResponse({'message':'Customer ID required.', 'status':False, 'status_code':400}, status=200)


    def put(self, request):
        id = request.data.get('id')
        if id:
            user = User.objects.filter(id=id).last()
            if user:
                serializer = UserSerialzer(user, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({'message':'Subser Updated successfully ', 'status':True, 'status_code':200, 'subuser':serializer.data}, status=200)
                return JsonResponse({'message':'Error during updating subuser', 'status':False, 'status_code':400, 'error':serializer.errors}, status=200)
            return JsonResponse({'message':'Invalid Subuser.', 'status':False, 'status':False, 'status_code':400}, status=200)
        return JsonResponse({'message':'ID required.', 'status':False, 'status_code':400}, status=200)