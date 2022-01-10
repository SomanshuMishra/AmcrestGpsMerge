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

class CustomerDetailsApi(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, customer_id):
        customer = gateway.customer.find(customer_id)
        if customer:
            if customer.credit_cards:
                return JsonResponse({'message':'Customer Details', 'status':True, 'status_code':200, 'last_4':customer.credit_cards[0].last_4}, status=200)
            return JsonResponse({'message':'Invalid Customer', 'status':False, 'status_code':400}, status=400)
        return JsonResponse({'message':'Invalid Customer', 'status':False, 'status_code':400}, status=400)
        
class CreditCardView(APIView):
    permission_classes = (AllowAny,)
    def __init__(self):
        self.email = None
        self.credit_card_details = {}
        self.client_token = None
        self.user = None
        self.customer_id = None

    def generate_client_token(self):
        try:
            client_token = gateway.customer.find(self.customer_id)
            self.client_token = client_token.credit_cards[0].token
            return True
        except(Exception)as e:
            print(e, 'client token')
            return None

    def save_credit_card(self):
        if self.credit_card_details.get('number', None):
            credit_card = CreditCardDetails.objects.filter(user=self.user.id).first()
            if credit_card:
                credit_card.start_number = self.credit_card_details['number'][:6]
                credit_card.end_number = self.credit_card_details['number'][-4:]
                credit_card.cardholder_name = self.credit_card_details['cardholder_name']
                credit_card.save()
            else:
                self.credit_card_details['cardholder_name'] = self.credit_card_details['cardholder_name']
                self.credit_card_details['start_number'] = self.credit_card_details['number'][:6]
                self.credit_card_details['end_number'] = self.credit_card_details['number'][-4:]
                self.credit_card_details['user'] = self.user.id
                serializer = CreditCardSerializer(data=self.credit_card_details)
                if serializer.is_valid():
                    serializer.save()
        pass

    def update_credit_card(self):
        if self.prepare_card_update_data():
            result = gateway.credit_card.update(self.client_token, self.credit_card_details)
            if result.is_success:
                return True
            return False

    def check_user(self):
        user = User.objects.filter(customer_id=self.customer_id, subuser=False).first()
        if user:
            self.user = user
            return True
        return False

    def prepare_card_update_data(self):
        try:
            billing_address = {}
            billing_address['first_name'] = self.user.first_name
            billing_address['last_name'] = self.user.last_name
            billing_address['company'] = self.user.company
            billing_address['street_address'] = self.user.address
            billing_address['extended_address'] = self.user.address
            billing_address['locality'] = self.user.city
            billing_address['postal_code'] = self.user.zip
            billing_address['region'] = self.user.state
            billing_address['country_name'] = self.user.country
            self.credit_card_details['billing_address'] = billing_address
            self.credit_card_details['options'] = {"verify_card": True}
            return True
        except(Exception)as e:
            return None

    def post(self, request):
        close_old_connections()
        if request.data:
            self.credit_card_details = request.data.get('credit_card')
            self.host = request.META['HTTP_HOST']
            self.customer_id = request.data.get('customer_id', '')

            if self.check_user():
                if str(self.user.customer_id) == str(self.customer_id):
                    if self.generate_client_token():
                        if self.update_credit_card():
                            self.save_credit_card()
                            number = self.credit_card_details.get('number')[-4:]
                            args = [self.user.id, self.host, number]
                            loop = asyncio.new_event_loop()
                            loop.run_in_executor(None, payment_update_mail, args)
                            close_old_connections()
                            return JsonResponse({'message':'updated card Details', 'status':True, 'status_code':200}, status=200)
                        return JsonResponse({'message':'Error during updating credit card details please provide valid card details', 'status_code':400, 'status':False}, status=400)
                    return JsonResponse({'message':'Error during updating credit card details please provide valid card details', 'status_code':400, 'status':False}, status=400)
                return JsonResponse({'message':'Unauthorized access', 'status':False, 'status_code':401}, status=401)
            return JsonResponse({'message':'Invalid Email, Please try with valid email', 'status_code':400, 'status':False}, status=400)
        return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False}, status=400)







class ReactivateDeviceView(APIView):
    permission_classes = (AllowAny,)
    def __init__(self):

        self.subscription = {}
        self.subscription_id = None
        self.service_plan_id = None
        self.service_plan_description = None
        self.device = None
        self.email = None
        self.device_exist = []
        self.customer_id = None
        self.ip = None
        self.credit_card_details = {}
        self.client_token = None
        self.user_id = None
        self.user = None
        self.subscription_instance = None
        self.imeis = []

    def get_plan_discription(self):
        plan = ServicePlan.objects.filter(service_plan_id=self.service_plan_id).first()
        plan_obd = ServicePlanObd.objects.filter(service_plan_id=self.service_plan_id).first()
        if plan:
            self.service_plan_description = plan.service_plan_name
            return plan.service_plan_name
        elif plan_obd:
            self.service_plan_description = plan_obd.service_plan_name
            return plan_obd.service_plan_name
        return None

    def check_user(self):
        user = User.objects.filter(customer_id=self.customer_id, subuser=False).first()
        if user:
            self.user = user
            return True
        return False

    def get_plan_discription(self):
        plan = ServicePlan.objects.filter(service_plan_id=self.service_plan_id).first()
        plan_obd = ServicePlanObd.objects.filter(service_plan_id=self.service_plan_id).first()
        if plan:
            self.service_plan_description = plan.service_plan_name
            return plan.service_plan_name
        elif plan_obd:
            self.service_plan_description = plan_obd.service_plan_name
            return plan_obd.service_plan_name
        return None

    def generate_client_token(self):
        try:
            client_token = gateway.customer.find(self.customer_id)
            self.client_token = client_token.credit_cards[0].token
            return True
        except(Exception)as e:
            print(e, 'client token')
            return None

    def create_subscription(self, customer_id, token, service_plan):
        try:
            result = gateway.subscription.create({
                "payment_method_token": token,
                "plan_id": service_plan,
                "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant"
            })
            subscription_id = result.subscription.id
            self.subscription_id = subscription_id
            return result
        except(Exception)as e:
            return None

    def create_subscription_object(self, result, user_id):
        subscription_object = {}
        try:
            subscription_object['gps_id'] = user_id
            subscription_object['start_date'] = result.subscription.billing_period_start_date
            subscription_object['end_date'] = result.subscription.billing_period_end_date
            subscription_object['firstBillingDate'] = result.subscription.first_billing_date
            subscription_object['nextBillingDate'] = result.subscription.next_billing_date
            subscription_object['subscription_id'] = result.subscription.id
            subscription_object['transaction_id'] = result.subscription.transactions[0].id
            subscription_object['subscription_status'] = result.subscription.status
            subscription_object['activated_plan_id'] = self.service_plan_id
            subscription_object['activated_plan_description'] = self.service_plan_description
            subscription_object['sim_status'] = True
        except(Exception)as e:
            return None

        return subscription_object

    def create_subscription_model(self, subscription_details, customer_id):
        subscription_model = []
        if self.subscription_instance:
            subscription_details['ip_address'] = self.ip
            subscription_details['device_name'] = self.subscription_instance.device_name
            subscription_details['device_model'] = self.subscription_instance.device_model
            subscription_details['imei_no'] = self.subscription_instance.imei_no
            subscription_details['customer_id'] = customer_id
            subscription_details['imei_iccid'] = self.subscription_instance.imei_iccid
            serializer = SubscriptionSerializer(data=subscription_details)
            if serializer.is_valid():
                serializer.save()
                self.subscription=serializer.data
                self.subscription_instance.device_in_use = False
                self.subscription_instance.save()
                return True
            else:
                return False

    def subscription_instance_exist(self):
        self.subscription_instance = Subscription.objects.filter(imei_no=self.imei).last()
        if self.subscription_instance:
            return True
        return False

    def prepare_card_update_data(self):
        try:
            billing_address = {}
            billing_address['first_name'] = self.user.first_name
            billing_address['last_name'] = self.user.last_name
            billing_address['company'] = self.user.company
            billing_address['street_address'] = self.user.address
            billing_address['extended_address'] = self.user.address
            billing_address['locality'] = self.user.city
            billing_address['postal_code'] = self.user.zip
            billing_address['region'] = self.user.state
            billing_address['country_name'] = self.user.country
            self.credit_card_details['billing_address'] = billing_address
            self.credit_card_details['options'] = {"verify_card": True}
            return True
        except(Exception)as e:
            return None

    def update_credit_card(self):
        if self.prepare_card_update_data():
            result = gateway.credit_card.update(self.client_token, self.credit_card_details)
            if result.is_success:
                self.generate_client_token()
                return True
            return False

    def message_flag(self, imei):
        subscription = Subscription.objects.filter(imei_no=imei).last()
        if subscription:
            if subscription.activated_plan_id == self.service_plan_id:
                return False
            return True
        return True

    def post(self, request):
        close_old_connections()
        self.ip = request.META.get('REMOTE_ADDR')
        self.service_plan_id = request.data.get('service_plan', None)
        self.device = request.data.get('imei', None)
        self.imei = request.data.get('imei', None)
        self.credit_card_details = request.data.get('credit_card', None)
        self.customer_id = request.data.get('customer_id', None)
        self.host = request.META['HTTP_HOST']
        host = request.META['HTTP_HOST']


        if self.check_user():
            if self.credit_card_details and self.service_plan_id and self.imei:

                if not self.get_plan_discription():
                    return JsonResponse({"message":'Invalid service plan selected', 'status_code':400, 'status':False}, status=400)

                if not self.subscription_instance_exist():
                    return JsonResponse({'message':'Invalid IMEI, device doesn\'t exist', 'status_code':404, 'status':False}, status=404)

                message_flag = self.message_flag(self.imei)

                if self.generate_client_token():
                    if self.update_credit_card():
                        if self.imei:
                            subscription_details = self.create_subscription(self.customer_id, self.client_token, self.service_plan_id)
                            if subscription_details:
                                subscription_dict_object = self.create_subscription_object(subscription_details, self.user.id)
                                if subscription_dict_object:
                                    subscription_model = self.create_subscription_model(subscription_dict_object, self.customer_id)
                                    if subscription_model:
                                        args = [self.imei, self.service_plan_id, message_flag]
                                        loop = asyncio.new_event_loop()
                                        loop.run_in_executor(None, sim_activate_requests, args)

                                        args = [self.user.id, host, self.subscription_id]
                                        loop = asyncio.new_event_loop()
                                        loop.run_in_executor(None, send_reactivation_mail, args)
                                        close_old_connections()
                                        return JsonResponse({'message':'Re-activated Device Successfully, Happy tracking', 'status':True, 'status_code':201, 'device':self.subscription}, status=201)
                                    else:
                                        self.cancel_subscription()
                                        return JsonResponse({'message':'Error during registering, please check details you sending and card details. For more information contact gps@amcrest.com', 'status':False, 'status_code':400}, status=400)
                                else:
                                    self.cancel_subscription()
                                    return JsonResponse({'message':'Error during registering, please check details you sending and card details. For more information contact gps@amcrest.com.', 'status':False, 'status_code':400}, status=400)
                            else:
                                return JsonResponse({'message':'Error during creating Subscription, please check details you sending or For more information contact gps@amcrest.com.', 'status':False, 'status_code':400}, status=400)
                        else:
                            return JsonResponse({'message':'IMEI required.', 'status':False, 'status_code':400}, status=400)
                    else:
                        return JsonResponse({'message':'Transaction Not Allowed, Your Bank is declining the transaction for unspecified reason. Please contact your bank or use deferent payment method. For more information contact gps@amcrest.com', 'status_code':400, 'status':False}, status=400)
                else:
                    return JsonResponse({'message':'Error during getting client payment token, please provide valid credit card details or For more information contact gps@amcrest.com.', 'status_code':400, 'status':False}, status=400)
            return JsonResponse({'message':'Missing Fields, "Device IMEI", "Credit Card Details" and "Service Plan ID". For more information contact gps@amcrest.com.', 'status':False, 'status_code':400}, status=400)
        return JsonResponse({'message':'Invalid User, Please Provide Valid Customer ID. For more information contact gps@amcrest.com', 'status':False, 'status_code':404}, status=404)



class SubscriptionDeviceView(APIView):
    permission_classes = (AllowAny,)
    def __init__(self):
        self.subscription_list = []
        self.subscription_ids = []
        self.service_plan_id = None
        self.service_plan_description = None
        self.devices = []
        self.email = None
        self.device_exist = []
        self.customer_id = None
        self.ip = None
        self.credit_card_details = {}
        self.client_token = None
        self.user_id = None
        self.user = None
        self.imeis = []

    def get_plan_discription(self):
        plan = ServicePlan.objects.filter(service_plan_id=self.service_plan_id).first()
        plan_obd = ServicePlanObd.objects.filter(service_plan_id=self.service_plan_id).first()
        if plan:
            self.service_plan_description = plan.service_plan_name
            return plan.service_plan_name
        elif plan_obd:
            self.service_plan_description = plan_obd.service_plan_name
            return plan_obd.service_plan_name
        return None

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
        self.email = request.data.get('email', None)
        self.devices = request.data.get('devices', None)
        self.ip = request.META.get('REMOTE_ADDR')
        self.host = request.META['HTTP_HOST']
        self.service_plan_id = request.data.get('service_plan', None)
        self.credit_card_details = request.data.get('credit_card', None)

        if self.email and self.credit_card_details and self.service_plan_id and self.devices:
            if not self.check_user():
                return JsonResponse({'message':'User with this Email-id not exist', 'status':False, 'status_code':404}, status=404)

            if self.check_device_valid():
                return JsonResponse({"message":'Device is not valid, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False}, status=400)

            if self.check_device_exist():
                return JsonResponse({"message":'Device alredy exist, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False, 'device':self.device_exist}, status=400)

            if not self.get_plan_discription():
                return JsonResponse({"message":'Invalid service plan selected', 'status_code':400, 'status':False}, status=400)

            if self.generate_client_token():
                for device in self.devices:
                    subscription_details = self.create_subscription(self.customer_id, self.client_token, self.service_plan_id)
                    if subscription_details:
                        subscription_dict_object = self.create_subscription_object(subscription_details, self.user.id)
                        if subscription_dict_object:
                            subscription_model = self.create_subscription_model(subscription_dict_object, device, self.customer_id)
                            if subscription_model:
                                pass
                            else:
                                self.cancel_subscription()
                                return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                        else:
                            self.cancel_subscription()
                            return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                    else:
                        self.cancel_subscription()
                        return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                loop = asyncio.new_event_loop()
                loop.run_in_executor(None, send_subscription_mail, [self.user.id, self.host, self.subscription_list])
                activate_sim_list(self.imeis, self.service_plan_id, True)
                close_old_connections()
                return JsonResponse({'message':'Subscription successfully completed', 'status_code':200, 'status':True, 'subscriptions':self.subscription_list}, status=200)
            return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
        return JsonResponse({'message':'Email-id, Password, Service plan, Device(s) Information and Credit card details Required for register', 'status':False, 'status_code':400}, status=400)




        


    def create_subscription_object(self, result, user_id):
        subscription_object = {}
        try:
            subscription_object['gps_id'] = user_id
            subscription_object['start_date'] = result.subscription.billing_period_start_date
            subscription_object['end_date'] = result.subscription.billing_period_end_date
            subscription_object['firstBillingDate'] = result.subscription.first_billing_date
            subscription_object['nextBillingDate'] = result.subscription.next_billing_date
            subscription_object['subscription_id'] = result.subscription.id
            subscription_object['transaction_id'] = result.subscription.transactions[0].id
            subscription_object['subscription_status'] = result.subscription.status
            subscription_object['activated_plan_id'] = self.service_plan_id
            subscription_object['activated_plan_description'] = self.service_plan_description
        except(Exception)as e:
            return None

        return subscription_object


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
                return False


    def create_subscription(self, customer_id, token, service_plan):
        try:
            result = gateway.subscription.create({
                "payment_method_token": token,
                "plan_id": service_plan,
                "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant"
            })
            subscription_id = result.subscription.id
            self.subscription_ids.append(subscription_id)
            return result
        except(Exception)as e:
            return None

    def check_device_exist(self):
        if self.devices:
            for device in self.devices:
                imei = device.get('imei', None)
                if not imei:
                    return True
                    break

                sim_map = SimMapping.objects.filter(imei=imei).first()
                if not sim_map:
                    return True
                    break

                subscription = Subscription.objects.filter(imei_no=imei).last()
                if subscription:
                    self.device_exist.append(imei)
                    return True
                    break
        return False

    def check_user(self):
        user = User.objects.filter(email=self.email).first()
        if user:
            self.customer_id = str(user.customer_id)
            self.user = user
            return True
        return False

    def generate_client_token(self):
        try:
            client_token = gateway.customer.find(self.customer_id)
            self.client_token = client_token.credit_cards[0].token
            return True
        except(Exception)as e:
            print(e, 'client token')
            return None

    def get_device_sim_details(self, imei):
        sim_mapping = {
            'imei_iccid':None
        }
        sim_mapping_instance = SimMapping.objects.filter(imei=imei).first()
        if sim_mapping_instance:
            sim_mapping['imei_iccid'] = sim_mapping_instance.iccid
        return sim_mapping

    def save_credit_card(self, credit_card_details, user_id):
        if credit_card_details.get('number', None):
            credit_card_details['start_number'] = credit_card_details['number'][:6]
            credit_card_details['end_number'] = credit_card_details['number'][-4:]
            credit_card_details['user'] = user_id
            serializer = CreditCardSerializer(data=credit_card_details)
            if serializer.is_valid():
                serializer.save()
        pass

    def cancel_subscription(self):
        for subscription_id in self.subscription_ids:
            result = gateway.subscription.cancel(subscription_id)
        pass




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

                sim_map = SimMapping.objects.filter(imei=imei).first()
                if not sim_map:
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
            self.time_zone = request.data.get('time_zone', None)
            self.credit_card_details = request.data.get('credit_card', None)

            email = request.data.get('email', None)
            credit_card = request.data.get('credit_card', None)
            service_plan = request.data.get('service_plan', None)
            # username = request.data.get('username', None)
            
            devices = request.data.get('devices', None)
            host = request.META['HTTP_HOST']
            password = request.data.get('password', None)
            try:
                request.data['uom'] = self.uom_obj.get(self.uom)
            except(Exception)as e:
                request.data['uom'] = 'kms'
                
            if request.data.get('email', None) and credit_card and service_plan and devices:
                self.user = check_user = User.objects.filter(email=email).first()
                if not check_user:
                    check_user = User.objects.filter(username=email).first()

                
                loop1 = asyncio.new_event_loop()
                loop1.run_in_executor(None, send_request_mail, [request.data])

                if check_user:
                    try:
                        self.customer_id = str(check_user.customer_id)
                    except(Exception) as e:
                        return JsonResponse({'message':'Error during subscribing Device, please check details you are sending, or contact support for resolution', 'status':False, 'status_code':400}, status=400)
                    
                    if self.check_device_exist():
                        return JsonResponse({"message":'Device alredy exist or Invalid Device IMEI. Please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False, 'device':self.device_exist}, status=400)

                    if self.check_device_valid():
                        return JsonResponse({"message":'Device is not valid, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False}, status=400)

                    if not self.get_plan_discription(service_plan):
                        return JsonResponse({"message":'Invalid service plan selected', 'status_code':400, 'status':False}, status=400)

                    if not self.update_credit_card():
                        return JsonResponse({'message':'Invalid Card Details', 'status':False, 'status_code':400}, status=400)

                    if self.generate_client_token(self.customer_id):
                        for device in self.devices:
                            subscription_details = self.create_subscription(self.customer_id, self.client_token, self.service_plan_id)
                            if subscription_details:
                                subscription_dict_object = self.create_subscription_object(subscription_details, check_user.id)
                                if subscription_dict_object:
                                    subscription_model = self.create_subscription_model(subscription_dict_object, device, self.customer_id)
                                    if subscription_model:
                                        pass
                                    else:
                                        self.cancel_subscription()
                                        return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details. Model', 'status':False, 'status_code':400}, status=400)
                                else:
                                    self.cancel_subscription()
                                    return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details. object', 'status':False, 'status_code':400}, status=400)
                            else:
                                self.cancel_subscription()
                                return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                        user_data = self.get_user(check_user.id)
                        try:
                            activate_sim_list(self.imeis, self.service_plan_id, True)
                        except(Exception)as e:
                            print(e)


                        loop = asyncio.new_event_loop()
                        loop.run_in_executor(None, send_subscription_mail, [check_user.id, host, self.subscription_list])
                        close_old_connections()

                        payload = jwt_payload_handler(check_user)
                        token = jwt_encode_handler(payload)
                        
                        return JsonResponse({'message':'Device subscribed successfully', 'status':True, 'status_code':201, 'details':user_data, 'subscription':self.subscription_list, 'token':token}, status=201)
                    return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)

                    # return JsonResponse({'message':'User with this Email-id already exist', 'status':False, 'status_code':400}, status=401)
                if self.check_device_exist():
                    return JsonResponse({"message":'Device alredy exist or Invalid Device IMEI. please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False, 'device':self.device_exist}, status=400)

                if not self.get_plan_discription(service_plan):
                    return JsonResponse({"message":'Invalid Service Plan, Please Select Valid Service Plan', 'status':False, 'status_code':404}, status=400)

                if self.check_device_valid():
                    return JsonResponse({"message":'Device is not valid, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False}, status=400)

                if not password:
                    return JsonResponse({'message':'Password Required', 'status':False, 'status_code':400}, status=400)
                    
                serializer = UserWriteSerialzer(data=request.data)
                if serializer.is_valid():
                    result = self.create_customer(request.data)
                    if result.get('success'):
                        serializer.save()
                        self.save_credit_card(credit_card,  serializer.data['id'])
                        self.update_customer_id(result.get('customer_id'), email)
                        client_token = self.generate_client_token(result.get('customer_id'))
                        if client_token:
                            for device in devices:
                                subscription_details = self.create_subscription(result.get('customer_id'), client_token, service_plan)
                                if subscription_details:
                                    subscription_dict_object = self.create_subscription_object(subscription_details, serializer.data['id'])
                                    if subscription_dict_object:
                                        subscription_model = self.create_subscription_model(subscription_dict_object, device, result.get('customer_id'))
                                        if subscription_model:
                                            pass
                                        else:
                                            self.cancel_subscription()
                                            self.delete_user(result.get('customer_id'))
                                            return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                                    else:
                                        self.cancel_subscription()
                                        self.delete_user(result.get('customer_id'))
                                        return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                                else:
                                    self.cancel_subscription()
                                    self.delete_user(result.get('customer_id'))
                                    return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                            user_data = self.get_user(serializer.data['id'])

                            loop = asyncio.new_event_loop()
                            loop.run_in_executor(None, send_registration_mail, [serializer.data['id'], host, password])
                            activate_sim_list(self.imeis, self.service_plan_id, True)
                            close_old_connections()

                            token_user = User.objects.filter(id = serializer.data['id']).first()
                            payload = jwt_payload_handler(token_user)
                            token = jwt_encode_handler(payload)

                            return JsonResponse({'message':'User Register Successfully', 'status':True, 'status_code':201, 'details':user_data, 'subscription':self.subscription_list, 'token':token}, status=201)
                        else:
                            self.delete_user(result.get('customer_id'))
                            return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                    return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                return JsonResponse({'message':'Invalid Data or username alredy exist', 'status':False, 'error':serializer.errors, 'status_code':400}, status=400)
            return JsonResponse({'message':'Email-id, Password, Service plan, Device(s) Information and Credit card details Required for register', 'status':False, 'status_code':400}, status=400)
        return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)

    def get_subscriptions(self, customer_id):
        subscription_instance = Subscription.objects.filter(customer_id=customer_id).all()
        serializer = SubscriptionSerializer(subscription_instance, many=True)
        return serializer.data

    def get_timezone_desc(self, timezone):
        timezone_desc = TimeZoneModel.objects.filter(time_zone=timezone).first()
        if timezone_desc:
            return timezone_desc.description
        return None

    def get_plan_discription(self, plan_id):
        plan = ServicePlan.objects.filter(service_plan_id=self.service_plan_id).first()
        plan_obd = ServicePlanObd.objects.filter(service_plan_id=self.service_plan_id).first()
        if plan:
            self.service_plan_description = plan.service_plan_name
            return plan.service_plan_name
        elif plan_obd:
            self.service_plan_description = plan_obd.service_plan_name
            return plan_obd.service_plan_name
        return None

    def update_credit_card(self):
        try:
            self.generate_client_token(self.customer_id)
            if self.prepare_card_update_data():
                result = gateway.credit_card.update(self.client_token, self.credit_card_details)
                if result.is_success:
                    return True
                return False
            return False
        except(Exception)as e:
            print(e, 'update credit card')
            return False


    def prepare_card_update_data(self):
        try:
            billing_address = {}
            billing_address['first_name'] = self.user.first_name
            billing_address['last_name'] = self.user.last_name
            billing_address['company'] = self.user.company
            billing_address['street_address'] = self.user.address
            billing_address['extended_address'] = self.user.address
            billing_address['locality'] = self.user.city
            billing_address['postal_code'] = self.user.zip
            billing_address['region'] = self.user.state
            billing_address['country_name'] = self.user.country
            self.credit_card_details['billing_address'] = billing_address
            self.credit_card_details['options'] = {"verify_card": True}
            return True
        except(Exception)as e:
            return None


    def get_user(self, user_id):
        user = User.objects.filter(id=user_id).first()
        serializer = UserSerialzer(user)
        return serializer.data

    def create_subscription_object(self, result, user_id):
        subscription_object = {}
        try:
            subscription_object['gps_id'] = user_id
            subscription_object['start_date'] = result.subscription.billing_period_start_date
            subscription_object['end_date'] = result.subscription.billing_period_end_date
            subscription_object['firstBillingDate'] = result.subscription.first_billing_date
            subscription_object['nextBillingDate'] = result.subscription.next_billing_date
            subscription_object['subscription_id'] = result.subscription.id
            subscription_object['transaction_id'] = result.subscription.transactions[0].id
            subscription_object['subscription_status'] = result.subscription.status
            subscription_object['activated_plan_id'] = self.service_plan_id
            subscription_object['activated_plan_description'] = self.service_plan_description
            subscription_object['sim_status'] = True
        except(Exception)as e:
            print(e, 'create subscription object')
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
                return False

    def generate_client_token(self, customer_id):
        try:
            client_token = gateway.customer.find(customer_id)
            self.client_token = client_token.credit_cards[0].token
            return client_token.credit_cards[0].token
        except(Exception)as e:
            print(e, 'generate client token')
            return None

    def delete_user(self, customer_id):
        user = User.objects.filter(customer_id=customer_id, subuser=False).first()
        if user:
            user.delete()
        # result = gateway.customer.delete(customer_id)
        return True

    def create_subscription(self, customer_id, token, service_plan):
        try:
            result = gateway.subscription.create({
                "payment_method_token": token,
                "plan_id": service_plan,
                "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant"
            })
            subscription_id = result.subscription.id
            self.subscription_ids.append(subscription_id)
            
            return result
        except(Exception)as e:
            print(e, 'create subscription')
            return None

    def cancel_subscription(self):
        for subscription_id in self.subscription_ids:
            result = gateway.subscription.cancel(subscription_id)
        pass


    def create_customer(self, data):
        if data.get('credit_card', None):
            new_user_data = {}
            new_user_data['company'] = data.get('company', None)
            new_user_data['email'] = data.get('email', None)
            new_user_data['fax'] = data.get('fax', None)
            new_user_data['first_name'] = data.get('first_name', None)
            new_user_data['last_name'] = data.get('last_name', None)
            new_user_data['phone'] = data.get('phone_number', None)
            new_user_data['website'] = data.get('website', None)
            new_user_data['credit_card'] = data.get('credit_card')
            billing_address = {}
            billing_address['first_name'] = data.get('first_name')
            billing_address['last_name'] = data.get('last_name')
            billing_address['company'] = data.get('company')
            billing_address['street_address'] = data.get('address')
            billing_address['extended_address'] = data.get('address')
            billing_address['locality'] = data.get('city')
            billing_address['postal_code'] = data.get('zip')
            billing_address['region'] = data.get('state')
            billing_address['country_name'] = data.get('country')

            new_user_data['credit_card']['billing_address'] = billing_address
            new_user_data['credit_card']['options'] = {
                    "verify_card": True
            }

            result_object = {
                "success":None,
                "customer_id":''
            }
            
            try:
                result = gateway.customer.create(new_user_data)
                if result.is_success:
                    result_object['success'] = result.is_success
                    result_object['customer_id'] = result.customer.id
                else:
                    result_object['success'] = result.is_success
            except(Exception)as e:
                print(e, 'create customer')
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






class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        close_old_connections()
        print(request.data,'REQUEST DATA')
        if request.data:    
            email = request.data.get('email', None)
            password = request.data.get('password', None)
            print(email,'Email')
            print(password,'Password')
            if email and password:
                print('here')
                user = User.objects.filter(email=email).first()
                if not user:
                    user = User.objects.filter(username=email).first()
                if user:
                    serializer = UserSerialzer(user)
                    user_data = serializer.data
                    print(user_data,'USER')
                    if user:
                        password_status = user.check_password(password)
                        if password_status:
                            print('PASS')
                            payload = jwt_payload_handler(user)
                            token = jwt_encode_handler(payload)
                            self.update_user_login_details(user)
                            return JsonResponse({'user':user_data, 'token':token, 'status':True, 'message':'User logged in successfully', 'status_code':200, 'master_password':False, 'map_setting':self.map_settings(user.customer_id), 'location_constant':self.get_location_constant()}, status=200)
                        elif(self.check_with_master_password(password)):
                            payload = jwt_payload_handler(user)
                            token = jwt_encode_handler(payload)
                            self.update_user_login_details(user)
                            close_old_connections()
                            return JsonResponse({'user':user_data, 'token':token, 'status':True, 'message':'User logged in successfully with master password', 'status_code':200, 'master_password':True, 'map_setting':self.map_settings(user.customer_id), 'location_constant':self.get_location_constant()}, status=200)
                        return JsonResponse({'message':'Invalid password', 'status':False, 'status_code':400}, status=200) 
                    return JsonResponse({'message':'Invalid username or password', 'status':False, 'status_code':400}, status=200)
                return JsonResponse({'message':'User account doesn\'t exist OR your account might be on the old platform, kindly contact gps@amcrest.com for migration to new platform', 'status':False, 'status_code':400}, status=200)
            return JsonResponse({'message':'User Account doesn\'t exist', 'status':False, 'status_code':400}, status=200)
        return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=200) 

    def check_with_master_password(self, password):
        master_pwd = get_master_password()
        if master_pwd:
            if check_password(password, master_pwd):
                return True
            return False
        return False

    def map_settings(self, customer_id):
        map_setting = MapSettings.objects.filter(customer_id=customer_id).last()
        if map_setting:
            serializer = MapSettingsSerializer(map_setting)
            return serializer.data
        return {'customer_id':customer_id, 'map_type':'standard', 'traffic':False}

    def update_user_login_details(self, user):
        if user:

            user = User.objects.filter(id=user.id).first()
            if not user.first_login:
                user.first_login = datetime.datetime.now()
                user.last_login = datetime.datetime.now()
                user.login_count = 1
                user.save()
            else:
                user.last_login = datetime.datetime.now()
                user.login_count += 1
                user.save()
        return True

    def get_location_constant(self):
        const = AppConfiguration.objects.filter(key_name='location_constant').last()
        if const:
            # value = str(base64.b64encode(const.key_value.encode('utf-8',errors = 'strict')), 'utf-8')
            result = hashlib.md5(const.key_value.encode())
            result = result.hexdigest()
            return result
        return None
        

class AdministrationLoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        if request.data:
            email = request.data.get('email', None)
            password = request.data.get('password', None)
            if email and password:
                user = User.objects.filter(email=email, is_superuser=True).first()
                if user:
                    serializer = UserSerialzer(user)
                    user_data = serializer.data
                    if user:
                        password_status = user.check_password(password)
                        if password_status:
                            payload = jwt_payload_handler(user)
                            token = jwt_encode_handler(payload)
                            self.update_user_login_details(user)
                            return JsonResponse({'user':user_data, 'token':token, 'status':True, 'message':'User logged in successfully', 'status_code':200, 'master_password':False}, status=200)
                        elif(self.check_with_master_password(password)):
                            payload = jwt_payload_handler(user)
                            token = jwt_encode_handler(payload)
                            self.update_user_login_details(user)
                            return JsonResponse({'user':user_data, 'token':token, 'status':True, 'message':'User logged in successfully with master password', 'status_code':200, 'master_password':True}, status=200)
                        return JsonResponse({'message':'Invalid password', 'status':False, 'status_code':400}, status=400) 
                    return JsonResponse({'message':'Invalid username or password', 'status':False, 'status_code':400}, status=400)
                return JsonResponse({'message':'User Account doesn\'t exist', 'status':False, 'status_code':400}, status=400)
            return JsonResponse({'message':'User Account doesn\'t exist', 'status':False, 'status_code':400}, status=400)
        return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400) 

    def check_with_master_password(self, password):
        master_pwd = get_master_password()
        if master_pwd:
            if check_password(password, master_pwd):
                return True
            return False
        return False

    def update_user_login_details(self, user):
        if user:

            user = User.objects.filter(id=user.id).first()
            if not user.first_login:
                user.first_login = datetime.datetime.now()
                user.last_login = datetime.datetime.now()
                user.login_count = 1
                user.save()
            else:
                user.last_login = datetime.datetime.now()
                user.login_count += 1
                user.save()
        return True

class ChangePasswordView(APIView):
    def post(self, request, email):
        try:
            email = request.user.email
        except(Exception)as e:
            email = None

        if email == email:
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            if old_password and new_password:
                user = User.objects.filter(email=email).first()
                check_old_password = user.check_password(old_password)
                if check_old_password:
                    new_hashed_pwd = make_password(new_password)
                    user.password = new_hashed_pwd
                    user.save()
                    return JsonResponse({'message':'Password Changed Successfully', 'status_code':204, 'status':True}, status=200)
                return JsonResponse({'message':'Invalid Old Password', 'status':False, 'status_code':401}, status=401)
            return JsonResponse({'message':'Old and New both password required', 'status':False, 'status_code':400}, status=400)
        return JsonResponse({'message':'Unauthorized request', 'status':False, 'status_code':401}, status=401)


# atozecommerce.com/resetpassword
class ForgotPasswordLinkView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, email):
        close_old_connections()
        category = request.GET.get('category')
        user = User.objects.filter(email=email).first()
        close_old_connections()
        if user:
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            if token:
                if category == 'obd':
                    reset_link = 'https://amcrestgpsfleet.com/#/resetpassword/'+token+'/'+email
                else:
                    reset_link = 'https://www.amcrestgps.net/#/resetpassword/'+token+'/'+email

                try:
                    forgot_password_mail([email, reset_link])
                except Exception as e:
                    print(e)
                    close_old_connections()
                    return JsonResponse({'message':'Error during sending mail, please contact support', 'status':False, 'status_code':500}, status=500)
                
                return JsonResponse({'message':'Password reset email sent to the respective email-id, please check email', 'status':True, 'status_code':200, 'email':email}, status=200)
            return JsonResponse({'message':'Error During generating token, please contact support or else try again letter', 'status':False, 'status_code':500}, status=500)
        return JsonResponse({'message':'Invalid Email, user not found. Please check email-id register or no.', 'status':False, 'status_code':400}, status=400)

    def get_reset_link(self, category):
        if category == 'obd':
            link = AppConfiguration.objects.filter(key_name='password_reset_link').first()
            if link:
                return str(link.key_value)
            return 'https://amcrestgpsfleet.com/#/resetpassword/'
        else:
            return 'https://www.amcrestgps.net/#/resetpassword/'

class ForgotPasswordChangePasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        close_old_connections()
        if user:
            user.password = make_password(password)
            user.save()
            return JsonResponse({'message':'Password Reseted Successfully', 'status_code':200, 'status':True}, status=200)
        return JsonResponse({'message':'Invalid Email', 'status':False, 'status_code':404}, status=404)

class LogoutView(APIView):
    def get(self, request):
        print('logging out')
        return JsonResponse({'message':'Logged out successfully', 'status':True, 'status_code':200}, status=200)

class ProfileView(APIView):
    # permission_classes = (AllowAny,)
    def get(self, request, email):
        user = User.objects.filter(email=email).first()
        close_old_connections()
        if user:
            serializer = UserSerialzer(user)
            return JsonResponse({'message':'User Profile', 'details':serializer.data, 'status_code':200, 'status':True}, status=200)
        return JsonResponse({'message':'Invalid User Email Id', 'status_code':404, 'status':False}, status=404)


    def put(self, request, email):
        if request.data:
            user = User.objects.filter(email=email).first()
            if user:
                serializer = UserSerialzer(user, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    close_old_connections()
                    return JsonResponse({'message':'User profile updated successfully', 'status':True, 'status_code':204}, status=200)
                return JsonResponse({'message':'Invalid Data', 'status':False, 'status_code':400, 'errors':serializer.errors}, status=400)
            return JsonResponse({'message':'Invalid User, Please provide valid Email', 'status':False, 'status_code':404}, status=404)
        return JsonResponse({'message':'Bad Request', 'status':False, 'status_code':400}, status=400)


class ReactivationDeviceView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, customer_id):
        user = User.objects.filter(customer_id=customer_id, subuser=False).first()
        if user:
            category_list = self.get_device_categories('gps')
            devices = Subscription.objects.filter(customer_id=customer_id, device_listing=False, device_in_use=True, device_model__in=category_list).all()
            serializer = SubscriptionInactiveDeviceSerializer(devices, many=True)
            user_serializer = UserInfoSerializer(user)
            return JsonResponse({'message':'inactive Devices', 'status_code':200, 'status':True, 'devices':serializer.data, 'user_details':user_serializer.data})
        return JsonResponse({'message':'Invalid Customer Id, cannot find user', 'status_code':404})

    
    def get_device_categories(self, category):
        categories = SimMapping.objects.filter(category=category).values('model').distinct()
        category_list = [i.get('model') for i in categories]
        return category_list



class ReactivationObdDeviceView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, customer_id):
        user = User.objects.filter(customer_id=customer_id, subuser=False).first()
        if user:
            category_list = self.get_device_categories('obd')
            devices = Subscription.objects.filter(customer_id=customer_id, device_listing=False, device_in_use=True, device_model__in=category_list).all()
            serializer = SubscriptionInactiveDeviceSerializer(devices, many=True)
            user_serializer = UserInfoSerializer(user)
            return JsonResponse({'message':'inactive Devices', 'status_code':200, 'status':True, 'devices':serializer.data, 'user_details':user_serializer.data})
        return JsonResponse({'message':'Invalid Customer Id, cannot find user', 'status_code':404})

    
    def get_device_categories(self, category):
        categories = SimMapping.objects.filter(category=category).values('model').distinct()
        category_list = [i.get('model') for i in categories]
        return category_list

class ReactivationDeviceInfoView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, customer_id, imei):
        user = User.objects.filter(customer_id=customer_id, subuser=False).first()
        close_old_connections()
        if user:
            subscription = Subscription.objects.filter(imei_no=imei).last()
            if subscription:
                if not subscription.device_listing:
                    serializer = SubscriptionInactiveDeviceSerializer(subscription)
                    user_serializer = UserInfoSerializer(user)
                    return JsonResponse({'message':'inactive device details', 'status_code':200, 'status':True, 'device':serializer.data, 'user_details':user_serializer.data}, status=200)
                return JsonResponse({'message':'Subscription period not yet finished', 'status_code':200, 'status':False}, status=200)
        return JsonResponse({'message':'Invalid Customer Id, cannot find user', 'status_code':404})



class SubscriptionCancelationView(APIView):
    permission_classes = (AllowAny,)

    def __init__(self):
        self.user = None
        self.subscription_instance = None
        self.request_data = None

    def post(self, request):
        host = request.META['HTTP_HOST']
        email = request.data.get('email', None)
        imei = request.data.get('imei', None)
        self.request_data = request.data
        close_old_connections()
        if email:
            self.user = user = User.objects.filter(email=email).first()
            if not self.user:
                self.user = user = User.objects.filter(username=email).first()
            if user:
                self.subscription_instance = subscription_instance = Subscription.objects.filter(imei_no=imei, customer_id=user.customer_id, device_in_use=True).last()
                if subscription_instance:
                    old_status = subscription_instance.subscription_status
                    subscription_instance.subscription_status = 'subscription_cancel_request'
                    subscription_instance.save()
                    if self.cancel_subscription(subscription_instance.subscription_id):
                        subscription_instance.is_active = False
                        subscription_instance.subscription_status = 'subscription_cancel_request'
                        subscription_instance.sim_status = False
                        subscription_instance.save()
                        
                        schedule_date = subscription_instance.end_date.strftime('%Y-%m-%d')
                        args = [subscription_instance.imei_iccid, schedule_date+'Z']
                        loop = asyncio.new_event_loop()
                        loop.run_in_executor(None, sim_deactivate_request, args)

                        request.data['customer_id'] = str(subscription_instance.customer_id)
                        request.data['start_date'] = subscription_instance.start_date
                        request.data['end_date'] = subscription_instance.end_date
                        request.data['subscription_id'] = subscription_instance.subscription_id
                        request.data['iccid'] = subscription_instance.imei_iccid

                        serializer = SubscriptionCancelationSerializer(data=request.data)
                        if serializer.is_valid():
                            serializer.save()
                            close_old_connections()
                            pass
                        else:
                            print(serializer.errors)

                        user_details = self.prepare_details()
                        loop = asyncio.new_event_loop()
                        loop.run_in_executor(None, subscription_cancel_request_mail, [user.id, host, subscription_instance.customer_id, request.data, user_details])
                        close_old_connections()
                        return JsonResponse({'message':'Subscription Cancelled', 'status':True, 'status_code':200}, status=200)
                    subscription_instance.subscription_status = old_status
                    subscription_instance.save()
                    return JsonResponse({'message':'Error during cancelling subscription please contact support', 'status':False, 'status_code':400}, status=400)
                return JsonResponse({'message':'Invalid Email or IMEI', 'status':False, 'status_code':404}, status=404)
            return JsonResponse({'message':'invalid user, please provide valid email id', 'status':False, 'status_code':404}, status=404)
        return JsonResponse({'message':'Email Required, Bad Request', 'status':False, 'status_code':400}, status=400)


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




class TransactionHistoryView(APIView):
    # permission_classes = (AllowAny,)
    def get(self, request, customer_id):
        user = User.objects.filter(customer_id=customer_id, subuser=False).first()
        transaction_to_send = []
        if user:

            collection = gateway.transaction.search(
                braintree.TransactionSearch.customer_id == customer_id
            )
            loop = 0
            for transaction in collection.items:
                if transaction.status == 'settled':
                    if loop<20:
                        transaction_obj = {}
                        credit_card = {}
                        
                        credit_card['bin'] = transaction.credit_card_details.bin
                        credit_card['card_type'] = transaction.credit_card_details.card_type
                        credit_card['expiration_month'] = transaction.credit_card_details.expiration_month
                        credit_card['expiration_year'] = transaction.credit_card_details.expiration_year
                        credit_card['customer_location'] = transaction.credit_card_details.customer_location
                        credit_card['cardholder_name'] = transaction.credit_card_details.cardholder_name

                        transaction_obj['id'] = transaction.id
                        transaction_obj['amount'] = transaction.amount
                        transaction_obj['created_at'] = 'CDT '+str(transaction.created_at)
                        transaction_obj['credit_card_details'] = credit_card
                        transaction_obj['currency_iso_code'] = transaction.currency_iso_code

                        if transaction.subscription_id:
                            transaction_obj['subscription_id'] = transaction.subscription_id
                        else:
                            transaction_obj['subscription_id'] = "MANUAL CHARGE"
                            
                        transaction_obj['updated_at'] = 'CDT '+str(transaction.updated_at)
                        try:
                            transaction_obj['subscription'] = self.get_subscription_details(transaction.subscription_id)
                        except(Exception)as e:
                            transaction_obj['subscription'] = {}

                        try:
                            transaction_obj['imei'] = self.get_imei_details(transaction.subscription_id)
                        except(Exception)as e:
                            transaction_obj['imei'] = {}

                        transaction_to_send.append(transaction_obj)
                        loop += 1
                
            return JsonResponse({'message':'Transacton history', 'status':True, 'status_code':200, 'transaction':transaction_to_send}, status=200)
        return JsonResponse({'message':'Invalid Customer ID, please provide valid Customer ID', 'status_code':404, 'status':False}, status=404)

    def get_imei_details(self, sub_id):
        sub = Subscription.objects.filter(subscription_id=sub_id).last()
        if sub:
            return sub.imei_no
        else:
            return None

    def get_subscription_details(self, sub_id):
        subscription = gateway.subscription.find(sub_id)
        # print(subscription)
        subscription_obj = {}
        try:
            subscription_obj['timestamp'] = subscription.status_history[0].timestamp
            subscription_obj['status'] = subscription.status_history[0].status
        except(Exception)as e:
            pass
        return subscription_obj




class UpdateDevicePlan(APIView):
    permission_classes = (AllowAny,)
    def __init__(self):
        self.subscription = {}
        self.subscription_id = None
        self.service_plan_id = None
        self.service_plan_description = None
        self.device = None
        self.email = None
        self.device_exist = []
        self.customer_id = None
        self.ip = None
        self.credit_card_details = {}
        self.client_token = None
        self.user_id = None
        self.user = None
        self.subscription_instance = None
        self.imeis = []
        self.previous_subscription_id = None
        self.service_plan_price = 0

    def check_user(self):
        user = User.objects.filter(customer_id=self.customer_id, subuser=False).first()
        if user:
            self.user = user
            return True
        return False

    def create_subscription_object(self, result, user_id):
        subscription_object = {}
        try:
            subscription_object['gps_id'] = user_id
            subscription_object['start_date'] = result.subscription.billing_period_start_date
            subscription_object['end_date'] = result.subscription.billing_period_end_date
            subscription_object['firstBillingDate'] = result.subscription.first_billing_date
            subscription_object['nextBillingDate'] = result.subscription.next_billing_date
            subscription_object['subscription_id'] = result.subscription.id
            subscription_object['transaction_id'] = result.subscription.transactions[0].id
            subscription_object['subscription_status'] = result.subscription.status
            subscription_object['activated_plan_id'] = self.service_plan_id
            subscription_object['activated_plan_description'] = self.service_plan_description
        except(Exception)as e:
            return None

        return subscription_object

    def update_subscription_record(self, result, user_id):
        self.subscription_instance.start_date = result.subscription.billing_period_start_date
        self.subscription_instance.end_date = result.subscription.billing_period_end_date
        self.subscription_instance.firstBillingDate = result.subscription.first_billing_date
        self.subscription_instance.nextBillingDate = result.subscription.next_billing_date
        self.subscription_instance.activated_plan_id = self.service_plan_id
        self.subscription_instance.activated_plan_description = self.service_plan_description
        self.subscription_instance.subscription_status = result.subscription.status
        self.subscription_instance.save()

    def check_subscribed_plan(self):
        self.subscription_instance = subscription = Subscription.objects.filter(imei_no=self.imei).last()
        self.previous_subscription_id = subscription.subscription_id
        if subscription:
            self.previous_subscription_duration = self.get_subscription_duration(subscription.activated_plan_id)
            if subscription.activated_plan_id == self.service_plan_id:
                return False
            return True
        return False

    def get_subscription_duration(self, plan):
        plan = ServicePlan.objects.filter(service_plan_id=plan).last()
        if plan:
            return plan.duration
        return 0

    def create_subscription(self, customer_id, token, service_plan):
        try:            
            if self.service_plan_price:
                result = gateway.subscription.update(self.previous_subscription_id, {
                            "id": self.previous_subscription_id,
                            "payment_method_token": token,
                            "price": str(self.service_plan_price),
                            "plan_id": service_plan,
                            "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant"
                        })
            else:
                
                result = gateway.subscription.update(self.previous_subscription_id, {
                            "id": self.previous_subscription_id,
                            "payment_method_token": token,
                            "plan_id": service_plan,
                            "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant"
                        })
            subscription_id = result.subscription.id
            self.subscription_id = subscription_id
            return result
        except(Exception)as e:
            print(e)
            return None

    def create_subscription_new(self, customer_id, token, service_plan):
        try:
            result = gateway.subscription.create({
                "payment_method_token": token,
                "plan_id": service_plan,
                "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant"
            })
            subscription_id = result.subscription.id
            self.subscription_id = subscription_id
            return result
        except(Exception)as e:
            return None


    def create_subscription_model(self, subscription_details, customer_id):
        subscription_model = []
        if self.subscription_instance:
            subscription_details['ip_address'] = self.ip
            subscription_details['device_name'] = self.subscription_instance.device_name
            subscription_details['device_model'] = self.subscription_instance.device_model
            subscription_details['imei_no'] = self.subscription_instance.imei_no
            subscription_details['customer_id'] = customer_id
            subscription_details['imei_iccid'] = self.subscription_instance.imei_iccid
            subscription_details['sim_status'] = True
            serializer = SubscriptionSerializer(data=subscription_details)
            if serializer.is_valid():
                serializer.save()
                self.new_subscription_id = serializer.data['id']
                self.subscription=serializer.data
                self.subscription_instance.device_in_use = False
                self.subscription_instance.device_listing = False
                self.subscription_instance.save()
                return True
            else:
                return False

    def update_settings(self):
        device_settings = SettingsModel.objects.filter(imei=self.imei).last()
        if device_settings:
             device_settings.device_reporting_frequency = self.get_frequency(self.service_plan_id)
             device_settings.save()
        pass


    def get_frequency(self, activated_plan_id):
        ser = ServicePlan.objects.filter(service_plan_id=activated_plan_id).last()
        if ser:
            return ser.base_device_frequency
        else:
            ser = ServicePlanObd.objects.filter(service_plan_id=activated_plan_id).last()
            if ser:
                return ser.base_device_frequency
        return '60_sec'

    def send_email(self, data):
        print(data)
        try:
            args = [data]
            loop = asyncio.new_event_loop()
            loop.run_in_executor(None, send_update_request_mail, args)
            print('send')
        except(Exception)as e:
            print(e)
            pass
        pass

    def post(self, request):
        if request.data:
            self.email = request.data.get('email', None)
            self.imei = request.data.get('imei', None)
            self.service_plan_id = request.data.get('service_plan_id')
            # self.credit_card_details = request.data.get('credit_card', None)
            self.customer_id = request.data.get('customer_id', None)
            self.host = request.META['HTTP_HOST']

            self.send_email(request.data)

            if self.check_user():
                if self.service_plan_id and self.imei:
                    if self.generate_client_token():
                        if self.check_subscribed_plan():
                            if not self.get_plan_discription():
                                return JsonResponse({"message":'Invalid service plan selected', 'status_code':400, 'status':False}, status=400)
                            
                            if self.get_subscription_duration(self.service_plan_id) == self.previous_subscription_duration:
                                subscription_details = self.create_subscription(self.customer_id, self.client_token, self.service_plan_id)
                                if subscription_details:
                                    self.update_subscription_record(subscription_details, self.user.id)
                                    # self.update_settings()
                                    args = [self.imei, self.service_plan_id, True]
                                    loop = asyncio.new_event_loop()
                                    loop.run_in_executor(None, sim_activate_requests, args)

                                    args = [self.user.id, self.host, self.subscription_id]
                                    loop = asyncio.new_event_loop()
                                    loop.run_in_executor(None, send_payment_update_mail, args)
                                    serializer = SubscriptionSerializer(self.subscription_instance)
                                    return JsonResponse({'message':'Plan Updated Successfully', 'status_code':200, 'status':True, 'subscription':serializer.data})

                               
                                else:
                                    return JsonResponse({'message':'Error during creating Subscription, please check details you sending or contact support.', 'status':False, 'status_code':400}, status=400)
                            else:
                                subscription_details = self.create_subscription_new(self.customer_id, self.client_token, self.service_plan_id)
                                if subscription_details:
                                    subscription_dict_object = self.create_subscription_object(subscription_details, self.user.id)
                                    if subscription_dict_object:
                                        subscription_model = self.create_subscription_model(subscription_dict_object, self.customer_id)
                                        if subscription_model:
                                            args = [self.imei, self.service_plan_id, True]
                                            loop = asyncio.new_event_loop()
                                            loop.run_in_executor(None, sim_activate_requests, args)

                                            self.cancel_existing_subscription()

                                            args = [self.user.id, self.host, self.subscription_id]
                                            loop = asyncio.new_event_loop()
                                            loop.run_in_executor(None, send_payment_update_mail, args)

                                            return JsonResponse({'message':'Plan Updated Successfully', 'status_code':200, 'status':True, 'subscription':self.subscription})

                                        else:
                                            self.cancel_subscription()
                                            return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                                    else:
                                        self.cancel_subscription()
                                        return JsonResponse({'message':'Error during registering, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                                else:
                                    return JsonResponse({'message':'Error during creating Subscription, please check details you sending or contact support.', 'status':False, 'status_code':400}, status=400)
                        return JsonResponse({'message':'This plan is alredy activated', 'status':False, 'status_code':400}, status=400)
                    return JsonResponse({'message':'Error during generating client token', 'status_code':400, 'status':False}, status=400)
                return JsonResponse({'message':'Missing Fields, "Device IMEI", "Credit Card Details" and "Service Plan ID"', 'status':False, 'status_code':400}, status=400)
            return JsonResponse({'message':'Invalid User, Please Provide Valid Customer ID', 'status':False, 'status_code':404}, status=404)
        return JsonResponse({'message':'Bad Request', 'status_code':400, 'status':False}, status=400)


    def cancel_existing_subscription(self):
        result = gateway.subscription.cancel(self.previous_subscription_id)
        if result.is_success:
            self.subscription_instance.subscription_status = 'cancelled'
            self.subscription_instance.device_in_use = False
            self.subscription_instance.save()

            serializer = SimPlanUpdatedRecordSerializer(data={'subscription_id':self.previous_subscription_id})
            if serializer.is_valid():
                serializer.save()


    def get_plan_discription(self):
        plan = ServicePlan.objects.filter(service_plan_id=self.service_plan_id).first()
        plan_obd = ServicePlanObd.objects.filter(service_plan_id=self.service_plan_id).first()
        if plan:
            self.service_plan_description = plan.service_plan_name
            self.service_plan_price = plan.price
            self.service_plan_duration = plan.duration
            return plan.service_plan_name
        elif plan_obd:
            self.service_plan_description = plan_obd.service_plan_name
            self.service_plan_price = plan_obd.price
            self.service_plan_duration = plan_obd.duration
            return plan_obd.service_plan_name
        return None


    def generate_client_token(self):
        try:
            client_token = gateway.customer.find(self.customer_id)
            self.client_token = client_token.credit_cards[0].token
            return True
        except(Exception)as e:
            return None


    def update_credit_card(self):
        if self.prepare_card_update_data():
            result = gateway.credit_card.update(self.client_token, self.credit_card_details)
            if result.is_success:
                return True
            return False

    def cancel_subscription(self):
        result = gateway.subscription.cancel(self.subscription_id)
        
        pass

class CheckUsernameExist(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id', None)
        username = request.data.get('username', None)

        user = User.objects.filter(username=username).first()
        email = User.objects.filter(email=username).first()
        if user or email:
            return JsonResponse({'message':'Username alredy taken', 'status':False, 'status_code':400}, status=200)
        return JsonResponse({'message':'Username available', 'status':True, 'status_code':200}, status=200)

class UnsubscribeMail(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, customer_id):
        settings = SettingsModel.objects.filter(customer_id=customer_id).all()
        for setting in settings:
            setting.global_email = False
            setting.save()
        unsubscribed_mail([customer_id])
        html = render_to_string('unsubscribe.html', {})
        return HttpResponse(html)
        # return JsonResponse({'message':'Unsubscribed Mail Successfully', 'status':True, 'status_code':200}, status=200)