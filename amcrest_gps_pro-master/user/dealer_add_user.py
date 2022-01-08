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



class DealerUserRegisterView(APIView):
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
            self.time_zone = request.data.get('time_zone', None)


            email = request.data.get('email', None)
            credit_card = request.data.get('credit_card', None)
            service_plan = request.data.get('service_plan', None)
            username = request.data.get('username', None)
            
            devices = request.data.get('devices', None)
            host = request.META['HTTP_HOST']
            password = request.data.get('password', None)

            request.data['emailing_address'] = request.data.get('email', None)
            domain = request.data.get('email', None).split('@')
            domain = domain[1]
            request.data['email'] = username+str(random.randint(0,1000000))+'@'+domain
            request.data['is_dealer_user'] = True

            try:
                request.data['uom'] = self.uom_obj.get(self.uom)
            except(Exception)as e:
                request.data['uom'] = 'kms'

            dealer_user = User.objects.filter(email=email).first()
            if not dealer_user:
                return JsonResponse({'message':'Invalid Dealer User', 'status':False, 'status_code':404}, status=200)

            if request.data.get('email', None) and credit_card and service_plan and devices:
                check_user = User.objects.filter(email=request.data.get('email', None)).first()
                if not check_user:
                    check_user = User.objects.filter(username=username).first()

                if check_user:
                    try:
                        self.customer_id = str(check_user.customer_id)
                    except(Exception) as e:
                        return JsonResponse({'message':'Error during subscribing Device, please check details you are sending, or contact support for resolution', 'status':False, 'status_code':400}, status=400)
                    
                    if self.check_device_exist():
                        return JsonResponse({"message":'Device alredy exist, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False, 'device':self.device_exist}, status=400)

                    if self.check_device_valid():
                        return JsonResponse({"message":'Device is not valid, please try with new IMEI or IMEI not provided', 'status_code':400, 'status':False}, status=400)

                    if not self.get_plan_discription(service_plan):
                        return JsonResponse({"message":'Invalid service plan selected', 'status_code':400, 'status':False}, status=400)

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
                                        print('subscription model')
                                        self.cancel_subscription()
                                        return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                                else:
                                    print('subscription_dict_object')
                                    self.cancel_subscription()
                                    return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                            else:
                                print('subscription_details')
                                self.cancel_subscription()
                                return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)
                        user_data = self.get_user(check_user.id)
                        try:
                            activate_sim_list(self.imeis, self.service_plan_id, True)
                        except(Exception)as e:
                            print(e)


                        loop = asyncio.new_event_loop()
                        loop.run_in_executor(None, send_dealer_subscription_mail, [check_user.id, host, self.subscription_list])
                        close_old_connections()

                        payload = jwt_payload_handler(check_user)
                        token = jwt_encode_handler(payload)
                        
                        dealer_serializer = DealerCustomersSerializer(data={'dealer':dealer_user.id, 'customer':check_user.id})
                        if dealer_serializer.is_valid():
                            dealer_serializer.save()
                        return JsonResponse({'message':'Device subscribed successfully', 'status':True, 'status_code':201, 'details':user_data, 'subscription':self.subscription_list, 'token':token}, status=201)
                    return JsonResponse({'message':'Error during subscribing devices, please check details you sending and card details.', 'status':False, 'status_code':400}, status=400)

                    # return JsonResponse({'message':'User with this Email-id already exist', 'status':False, 'status_code':400}, status=401)
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
                        self.save_credit_card(credit_card,  serializer.data['id'])
                        self.update_customer_id(result.get('customer_id'), serializer.data['email'])
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

                            loop = asyncio.new_event_loop()
                            loop.run_in_executor(None, send_dealer_registration_mail, [serializer.data['id'], host, password])
                            activate_sim_list(self.imeis, self.service_plan_id, True)
                            close_old_connections()

                            token_user = User.objects.filter(id = serializer.data['id']).first()
                            payload = jwt_payload_handler(token_user)
                            token = jwt_encode_handler(payload)

                            dealer_serializer = DealerCustomersSerializer(data={'dealer':dealer_user.id, 'customer':serializer.data['id']})
                            if dealer_serializer.is_valid():
                                dealer_serializer.save()

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
            print(client_token)
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

    def create_subscription(self, customer_id, token, service_plan):
        try:
            result = gateway.subscription.create({
                "payment_method_token": token,
                "plan_id": service_plan,
                "merchant_account_id" : "AmcrestTechnologiesGPSTracker_instant"
            })
            print(result)
            subscription_id = result.subscription.id
            self.subscription_ids.append(subscription_id)
            return result
        except(Exception)as e:
            print(e)
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




class DealerCustomerList(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, customer_id):
        if customer_id and customer_id != 'undefined':
            user = User.objects.filter(customer_id=customer_id).last()
            if user:
                customers = DealerCustomers.objects.filter(dealer=user.id).all()
                serializer = DealerCustomersReadSerializer(customers, many=True)
                result = self.get_subscriptions(serializer.data)
                return JsonResponse({'message':'Customer List', 'status':True, 'status_code':200, 'customer':result}, status=200)
            return JsonResponse({'message':'Invalid User', 'status':False, 'status_code':400, 'customer':[]}, status=200)
        return JsonResponse({'message':'Invalid User', 'status':False, 'status_code':400, 'customer':[]}, status=200)


    def get_subscriptions(self, data):
        result = []
        done = []
        for i in data:
            if i.get('customer', None):
                if i['customer'].get('customer_id', None) not in done:
                    i['customer']['subscriptions'] = []
                    subscriptions = Subscription.objects.filter(customer_id=i['customer'].get('customer_id', None)).all()
                    if subscriptions:
                        sub_serializer = SubscriptionSerializer(subscriptions, many=True)
                        i['customer']['subscriptions'] = sub_serializer.data
                    result.append(i)
                    done.append(i['customer'].get('customer_id', None))
        return result