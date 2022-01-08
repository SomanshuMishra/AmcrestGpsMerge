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


class UserRegisterView(APIView):
    permission_classes = (AllowAny,)
    def __init__(self):
        self.subscription_list = []
        self.subscription_ids = []
        self.service_plan_id = None
        self.service_plan_description = None
        self.ip = None
        self.devices = []
        self.customer_id = None
        self.client_token = None
        self.device_exist = []
        self.imeis = []
        self.uom = 'KMH'
        self.uom_obj = {
            'KMH':'kms',
            'MPH': 'miles' 
        }

    def generate_password(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))

    def check_device_exist(self):
        if self.devices:
            for device in self.devices:
                imei = device.get('imei', None)
                if not imei:
                    return True
                    break
                subscription = Subscription.objects.filter(imei_no=imei).last()
                if subscription:
                    self.device_exist.append(imei)
                    return True
                    break
        return False

    def check_device_valid(self):
        if self.devices:
            for device in self.devices:
                imei = device.get('imei', None)
                if not imei:
                    return True
                    break
                subscription = SimMapping.objects.filter(imei=imei).first()
                if not subscription:
                    return True
                    break

        return False

    def post(self, request):
        close_old_connections()
        if request.data:
            self.ip = request.META.get('REMOTE_ADDR')
            self.service_plan_id = request.data.get('service_plan', None)
            self.devices = request.data.get('devices', None)
            self.uom = request.data.get('uom', None)
            self.test_month = int(request.data.get('test_month', 30))
            # request.data['username'] = request.data.get('email', None)

            email = request.data.get('email', None)
            credit_card = request.data.get('credit_card', None)
            service_plan = request.data.get('service_plan', None)
            
            devices = request.data.get('devices', None)
            host = request.META['HTTP_HOST']
            password = request.data.get('password', None)
            try:
                request.data['uom'] = self.uom_obj.get(self.uom)
            except(Exception)as e:
                request.data['uom'] = 'kms'

            if request.data.get('email', None) and devices:
                if not User.objects.filter(email = email).first():
                    if self.check_device_exist():
                        return JsonResponse({"message":'Device alredy exist, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False, 'device':self.device_exist}, status=400)

                    if not self.get_plan_discription(service_plan):
                        return JsonResponse({"message":'Invalid Service Plan, Please Select Valid Service Plan', 'status':False, 'status_code':404}, status=400)

                    if self.check_device_valid():
                        return JsonResponse({"message":'Device is not valid, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False}, status=400)

                    serializer = UserWriteSerialzer(data=request.data)
                    if serializer.is_valid():
                        result = self.create_customer(request.data)
                        if result.get('success'):
                            serializer.save()
                            self.update_customer_id(result.get('customer_id'), email)
                            for device in devices:
                                subscription_details = self.create_subscription(result.get('customer_id'), service_plan)
                                if subscription_details:
                                    subscription_dict_object = self.create_subscription_object(subscription_details, serializer.data['id'])
                                    if subscription_dict_object:
                                        subscription_model = self.create_subscription_model(subscription_dict_object, device, result.get('customer_id'))
                                        if subscription_model:
                                            pass
                                        else:
                                            print('new user subscription_model')
                                            self.cancel_subscription()
                                            self.delete_user(result.get('customer_id'))
                                            return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                                    else:
                                        print('new user subscription_dict_object')
                                        self.cancel_subscription()
                                        self.delete_user(result.get('customer_id'))
                                        return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                                else:
                                    print('new user subscription_details')
                                    self.cancel_subscription()
                                    self.delete_user(result.get('customer_id'))
                                    return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                            user_data = self.get_user(serializer.data['id'])

                            activate_sim_list(self.imeis, self.service_plan_id, True)
                            
                            loop = asyncio.new_event_loop()
                            loop.run_in_executor(None, send_registration_mail, [serializer.data['id'], host, password])
                            
                            close_old_connections()

                            args = [self.subscription_list[0]['imei_iccid'], self.subscription_list[0]['end_date']+'Z']
                            loop = asyncio.new_event_loop()
                            loop.run_in_executor(None, sim_deactivate_request, args)

                            # token_user = User.objects.filter(id = serializer.data['id']).first()
                            # payload = jwt_payload_handler(token_user)
                            # token = jwt_encode_handler(payload)
                            return JsonResponse({'message':'User Register Successfully', 'status':True, 'status_code':201, 'details':user_data, 'subscription':self.subscription_list}, status=201)
                        return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                    return JsonResponse({'message':'Invalid Data', 'status':False, 'error':serializer.errors, 'status_code':400}, status=400)
                return JsonResponse({'message':'User alredy exist, Cannot register', 'status':False, 'status_code':400}, status=400)
            return JsonResponse({'message':'Email-id, Password, Service plan, Device(s) Information and Credit card details Required for register', 'status':False, 'status_code':400}, status=400)
        return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)

    def get_subscriptions(self, customer_id):
        subscription_instance = Subscription.objects.filter(customer_id=customer_id).all()
        serializer = SubscriptionSerializer(subscription_instance, many=True)
        return serializer.data

    def get_plan_discription(self, plan_id):
        self.service_plan_description = 'Beta Testing Plan'
        return 'Beta Test'



    def get_user(self, user_id):
        user = User.objects.filter(id=user_id).first()
        serializer = UserSerialzer(user)
        return serializer.data

    def create_subscription_object(self, result, user_id):
        subscription_object = {}
        today = datetime.datetime.now()
        last_date = today + datetime.timedelta(days = self.test_month)
        try:
            subscription_object['gps_id'] = user_id
            subscription_object['start_date'] = today.strftime('%Y-%m-%d')
            subscription_object['end_date'] = last_date.strftime('%Y-%m-%d')
            subscription_object['firstBillingDate'] = today.strftime('%Y-%m-%d')
            subscription_object['nextBillingDate'] = last_date.strftime('%Y-%m-%d')
            subscription_object['subscription_id'] = 'beta_test'
            subscription_object['transaction_id'] = 'beta_test'
            subscription_object['subscription_status'] = 'Active'
            subscription_object['activated_plan_id'] = 'beta_test'
            subscription_object['activated_plan_description'] = self.service_plan_description
            subscription_object['sim_status'] = True
        except(Exception)as e:
            print(e)
            return None

        return subscription_object

    def get_device_sim_details(self, imei):
        sim_mapping = {
            'imei_iccid':None
        }
        sim_mapping_instance = SimMapping.objects.filter(imei=imei).first()
        if sim_mapping_instance:
            sim_mapping['imei_iccid'] = sim_mapping_instance.iccid
        return sim_mapping




    def create_subscription_model(self, subscription_details, device, customer_id):
        subscription_model = []
        if device:
            sim_mapping = self.get_device_sim_details(device.get('imei', None))
            subscription_details['ip_address'] = self.ip
            subscription_details['device_name'] = device.get('device_name', None)
            subscription_details['device_model'] = device.get('device_model', None)
            subscription_details['imei_no'] = device.get('imei', None)
            subscription_details['customer_id'] = customer_id
            subscription_details['imei_iccid'] = sim_mapping['imei_iccid']
            serializer = SubscriptionSerializer(data=subscription_details)
            if serializer.is_valid():
                serializer.save()
                self.subscription_list.append(serializer.data)
                self.imeis.append(device.get('imei', None))
                return True
            else:
                print(serializer.errors)
                return False

    def generate_client_token(self, customer_id):
        try:
            client_token = gateway.customer.find(customer_id)
            self.client_token = client_token.credit_cards[0].token
            return client_token.credit_cards[0].token
        except(Exception)as e:
            print(e)
            return None

    def delete_user(self, customer_id):
        user = User.objects.filter(customer_id=customer_id).first()
        if user:
            user.delete()
        result = gateway.customer.delete(customer_id)
        return True

    def create_subscription(self, customer_id, service_plan):
        try:
            subscription_id = 'beta_test_'+str(customer_id)
            self.subscription_ids.append(subscription_id)
            return {'subscription_id':subscription_id}
        except(Exception)as e:
            print(e)
            return None

    def cancel_subscription(self):
        for subscription_id in self.subscription_ids:
            try:
                result = gateway.subscription.cancel(subscription_id)
            except(Exception)as e:
                pass
        pass


    def create_customer(self, data):
        # if data.get('credit_card', None):
        new_user_data = {}
        new_user_data['company'] = data.get('company', None)
        new_user_data['email'] = data.get('email', None)
        new_user_data['fax'] = data.get('fax', None)
        new_user_data['first_name'] = data.get('first_name', None)
        new_user_data['last_name'] = data.get('last_name', None)
        new_user_data['phone'] = data.get('phone_number', None)
        new_user_data['website'] = data.get('website', None)
        
        result_object = {
            "success":None,
            "customer_id":''
        }
        
        try:
            result = gateway.customer.create(new_user_data)
            print(result)
            if result.is_success:
                result_object['success'] = result.is_success
                result_object['customer_id'] = result.customer.id
            else:
                result_object['success'] = result.is_success
        except(Exception)as e:
            print(e)
            result_object['success'] = False
            
        return result_object

    def update_customer_id(self, customer_id=None, email=None):
        if email and customer_id:
            user = User.objects.filter(email=email).first()
            if user:
                user.customer_id = customer_id
                user.save()
            else:
                pass
        else:
            pass


    def save_credit_card(self, credit_card_details, user_id):
        if credit_card_details.get('number', None):
            credit_card_details['start_number'] = credit_card_details['number'][:6]
            credit_card_details['end_number'] = credit_card_details['number'][-4:]
            credit_card_details['user'] = user_id
            serializer = CreditCardSerializer(data=credit_card_details)
            if serializer.is_valid():
                serializer.save()
        pass


class AddToExistingView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        email = request.data.get('email', None)
        imei = request.data.get('imei_no', None)
        device_name = request.data.get('device_name')
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)
        next_billing_date = request.data.get('nextBillingDate', None)
        customer_id = request.data.get('customer_id', None)
        subscription_id = request.data.get('subscription_id', None)
        transaction_id = request.data.get('transaction_id', None)
        subscription_status = request.data.get('subscription_status', None)
        plan_id = request.data.get('plan_id', None)

        if email and imei and device_name and start_date and end_date and customer_id and transaction_id and subscription_id and plan_id and subscription_status:
            user = User.objects.filter(email=email, customer_id=customer_id).last()
            if user:
                sim_mapping = SimMapping.objects.filter(imei=imei).last()
                if sim_mapping:
                    subscription = Subscription.objects.filter(subscription_id=subscription_id, customer_id=customer_id).last()
                    subscription_obj = {
                        "customer_id":customer_id,
                        "subscription_id": subscription_id,
                        "transaction_id" :  transaction_id,
                        "subscription_status" : subscription_status,
                        "imei_no" : imei,
                        "device_name" : device_name,
                        "device_model" : sim_mapping.model,
                        "imei_iccid" : sim_mapping.iccid,
                        "sim_status" : True,
                        "start_date" : start_date,
                        "end_date" : end_date,
                        "nextBillingDate" : next_billing_date,
                        "activated_plan_id" : plan_id,
                        "activated_plan_description" : self.get_plan_discription(plan_id)
                    }
                    serializer = SubscriptionSerializer(data=subscription_obj)
                    if serializer.is_valid():
                        serializer.save()

                        args = [imei, plan_id, True]
                        loop = asyncio.new_event_loop()
                        loop.run_in_executor(None, sim_activate_requests, args)


                        if subscription:
                            subscription.is_active = False
                            subscription.device_listing = False
                            subscription.device_in_use = False
                            subscription.save()

                        return JsonResponse({'message':'Subscription Saved Successfully', 'status':True, 'status_code':200, 'subscription':serializer.data}, status=200)
                    else:
                        return JsonResponse({'message':'Error During saving subscription', 'status':True, 'status_code':400, 'error':serializer.errors}, status=400)
                else:
                    return JsonResponse({'message':'Invalid IMEI, Please try with a valid IMEI', 'status':False, 'status_code':200}, status=200)

            else:
                return JsonResponse({'message':'Sorry user doesn\'t exists', 'status':False, 'status_code':400}, status=400)
        else:
            return JsonResponse({'message':'Bad Request, All fields should be there', 'status':False, 'status_code':400}, status=400)



    def get_plan_discription(self, service_plan_id):
        plan = ServicePlan.objects.filter(service_plan_id=service_plan_id).first()
        plan_obd = ServicePlanObd.objects.filter(service_plan_id=service_plan_id).first()
        if plan:
            return plan.service_plan_name
        elif plan_obd:
            return plan_obd.service_plan_name
        return service_plan_id
                        # customer_id
                        # subscription_id
                        # transaction_id
                        # subscription_status
                        # imei_no
                        # device_name
                        # device_model
                        # imei_iccid
                        # sim_status
                        # start_date
                        # end_date
                        # firstBillingDate
                        # nextBillingDate
                        # activated_plan_id
                        # activated_plan_description