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
import os

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

from datetime import timedelta

from django.template.loader import render_to_string
from weasyprint import HTML, CSS

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


class InvoiceApiView(APIView):
    # permission_classes = (AllowAny,)
    def __init__(self):
        self.main_invoice_data = {
            'invoice_id':None,
            'plan_desc_1':'',
            'start_date_1': '',
            'end_date_1' : '',
            'amount_1':'',
            'subscription_id':'',
            'customer_name':'',
            'customer_mail_id':'',
            'customer_address':'',
            'customer_city':'',
            'customer_state':'',
            'customer_country':'',
            'plan_desc_2':'',
            'start_date_2': '',
            'end_date_2' : '',
            'amount_2':0,
            'line_2' : False
        }

    def post(self, request):
        email = request.data.get('email', None)
        self.category = request.GET.get('category', None)
        if email:
            user = User.objects.filter(email=email).first()
            transaction_to_send = []
            if user:
                self.main_invoice_data['customer_name'] = user.first_name+' '+user.last_name
                self.main_invoice_data['customer_mail_id'] = user.email
                self.main_invoice_data['customer_address'] = user.address
                self.main_invoice_data['customer_city'] = user.city
                self.main_invoice_data['customer_state'] = user.state
                self.main_invoice_data['customer_country'] = user.country

                collection = gateway.transaction.search(
                    braintree.TransactionSearch.customer_id == str(user.customer_id)
                )

                loop = 0
                for transaction in collection.items:
                    print(transaction)
                    if loop<1:
                        
                        if loop == 0:
                            self.main_invoice_data['invoice_id'] = transaction.id
                            self.main_invoice_data['invoice_date'] = datetime.datetime.now().strftime('%m/%d/%Y')
                            self.main_invoice_data['subscription_id'] = transaction.subscription_id
                            subscription_re = self.get_subscription_details(transaction.subscription_id)
                            self.main_invoice_data['plan_desc_1'] = subscription_re.get('plan', '')
                            self.main_invoice_data['start_date_1'] = transaction.subscription_details.billing_period_start_date.strftime('%m/%d/%Y')
                            self.main_invoice_data['end_date_1'] = transaction.subscription_details.billing_period_end_date.strftime('%m/%d/%Y')
                            self.main_invoice_data['amount_1'] = transaction.amount

                            try:
                                next_billing_date = transaction.subscription_details.billing_period_end_date + timedelta(days=1)
                                self.main_invoice_data['next_billing_date'] = next_billing_date.strftime('%m/%d/%Y')
                            except(Exception)as e:
                                next_billing_date = ''
                                self.main_invoice_data['next_billing_date'] = ''

                            self.main_invoice_data['credit_card_details'] = {
                                'last_4':transaction.credit_card_details.last_4,
                                'card_type':transaction.credit_card_details.card_type
                            }
                            self.main_invoice_data['status'] = transaction.status
                        elif loop == 1:
                            self.main_invoice_data['line_2'] = True
                            subscription_re = self.get_subscription_details(transaction.subscription_id)
                            self.main_invoice_data['plan_desc_2'] = subscription_re.get('plan', '')
                            self.main_invoice_data['start_date_2'] = transaction.subscription_details.billing_period_start_date.strftime('%m/%d/%Y')
                            self.main_invoice_data['end_date_2'] = transaction.subscription_details.billing_period_end_date.strftime('%m/%d/%Y')
                            self.main_invoice_data['amount_2'] = transaction.amount
                        loop += 1


                if self.main_invoice_data.get('invoice_id'):
                	# filename = 'user/invoices/invoice_{}.pdf'.format(self.main_invoice_data.get('invoice_id'))
                	filename = '/home/ubuntu/amcrest_gps_pro/user/invoices/invoice_{}.pdf'.format(self.main_invoice_data.get('invoice_id'))
                	encoded_string = ''

                	if self.category=='obd':
                		html_string = render_to_string('invoice_obd.html', self.main_invoice_data)
                		html = HTML(string=html_string)
	                	html.write_pdf(target=filename)
	                	send_obd_invoice_mail(user.email, filename)
                	else:
                		html_string = render_to_string('invoice.html', self.main_invoice_data)
	                	html = HTML(string=html_string)
	                	html.write_pdf(target=filename)
	                	send_gps_invoice_mail(user.email, filename)
	                os.remove(filename)
            return JsonResponse({'message':'Invoice Sent Successfully', 'status':True, 'status_code':200}, status=200)
        return JsonResponse({'message':'Bad Request, Email Required', 'status_code':200, 'status':False}, status=200)


    def get_subscription_details(self, sub_id):
        
        subscription_obj = {}
        try:
            subscription = gateway.subscription.find(sub_id)
            subscription_obj['timestamp'] = subscription.status_history[0].timestamp
            subscription_obj['status'] = subscription.status_history[0].status
            subscription_obj['billing_period_end_date'] = str(subscription.billing_period_end_date.month)+'/'+str(subscription.billing_period_end_date.day)+'/'+str(subscription.billing_period_end_date.year)
            subscription_obj['billing_period_start_date'] = str(subscription.billing_period_start_date.month)+'/'+str(subscription.billing_period_start_date.day)+'/'+str(subscription.billing_period_start_date.year)
            subscription_obj['next_billing_date'] = str(subscription.next_billing_date.month)+'/'+str(subscription.next_billing_date.day)+'/'+str(subscription.next_billing_date.year)
            subscription_obj['plan'] = self.get_plan_desc(subscription.plan_id)
        except(Exception)as e:
            print(e)
            pass
        return subscription_obj

    def get_plan_desc(self, plan_id):
    	if self.category == 'gps':
    		subscription_plan = ServicePlan.objects.filter(service_plan_id=plan_id).first()
    		if subscription_plan:
    			return subscription_plan.service_plan_name
    		return 'Amcrest GPS Pro Service'
    	else:
    		subscription_plan = ServicePlanObd.objects.filter(service_plan_id=plan_id).first()
    		if subscription_plan:
    			return subscription_plan.service_plan_name
    		return 'Amcrest GPS Fleet Service'



class InvoiceDownloadApiView(APIView):
    # permission_classes = (AllowAny,)
    def __init__(self):
        self.main_invoice_data = {
            'invoice_id':None,
            'plan_desc_1':'',
            'start_date_1': '',
            'end_date_1' : '',
            'amount_1':'',
            'customer_name':'',
            'customer_mail_id':'',
            'customer_address':'',
            'customer_city':'',
            'customer_state':'',
            'customer_country':'',
            'plan_desc_2':'',
            'start_date_2': '',
            'end_date_2' : '',
            'amount_2':0,
            'line_2' : False,
            'subscription_id':''
        }

    def post(self, request):
        email = request.data.get('email', None)
        self.category = request.GET.get('category', None)
        transaction_id = request.data.get('transaction_id')
        if email and transaction_id:
            user = User.objects.filter(email=email).first()
            transaction_to_send = []
            if user:
                self.main_invoice_data['customer_name'] = user.first_name+' '+user.last_name
                self.main_invoice_data['customer_mail_id'] = user.email
                self.main_invoice_data['customer_address'] = user.address
                self.main_invoice_data['customer_city'] = user.city
                self.main_invoice_data['customer_state'] = user.state
                self.main_invoice_data['customer_country'] = user.country

                try:
                    transaction = gateway.transaction.find(transaction_id)
                except(Exception)as e:
                    return JsonResponse({'message':'Sorry for inconvience, unable to find tranaction', 'status_code':400, 'status':False}, status=200)

                self.main_invoice_data['invoice_id'] = transaction.id
                self.main_invoice_data['invoice_date'] = datetime.datetime.now().strftime('%m/%d/%Y')

                if transaction.subscription_id:
                    self.main_invoice_data['subscription_id'] = transaction.subscription_id
                else:
                    self.main_invoice_data['subscription_id'] = ''

                if transaction.subscription_id:
                    subscription_re = self.get_subscription_details(transaction.subscription_id)
                    self.main_invoice_data['plan_desc_1'] = subscription_re.get('plan', '')
                    try:
                        self.main_invoice_data['start_date_1'] = transaction.subscription_details.billing_period_start_date.strftime('%m/%d/%Y')
                    except(Exception)as e:
                        self.main_invoice_data['start_date_1'] = ''

                    try:
                        self.main_invoice_data['end_date_1'] = transaction.subscription_details.billing_period_end_date.strftime('%m/%d/%Y')
                    except(Exception)as e:
                        self.main_invoice_data['end_date_1'] = ''

                    try:
                        self.main_invoice_data['amount_1'] = transaction.amount
                    except(Exception)as e:
                        self.main_invoice_data['amount_1'] = ''

                    try:
                        next_billing_date = transaction.subscription_details.billing_period_end_date + timedelta(days=1)
                    except(Exception)as e:
                        next_billing_date = ''

                    try:
                        self.main_invoice_data['next_billing_date'] = next_billing_date.strftime('%m/%d/%Y')
                    except(Exception)as e:
                        self.main_invoice_data['next_billing_date'] = ''
                else:
                    self.main_invoice_data['plan_desc_1'] = 'Manual Charge'
                    self.main_invoice_data['start_date_1'] = ''
                    self.main_invoice_data['end_date_1'] = ''
                    self.main_invoice_data['amount_1'] = transaction.amount
                    self.main_invoice_data['billing_date'] = transaction.created_at.strftime('%m/%d/%Y')
                    next_billing_date = None

                self.main_invoice_data['credit_card_details'] = {
                    'last_4':transaction.credit_card_details.last_4,
                    'card_type':transaction.credit_card_details.card_type
                }
                self.main_invoice_data['status'] = transaction.status

                print(self.main_invoice_data)
                if self.main_invoice_data.get('invoice_id'):
                	# filename = 'user/invoices/invoice_{}.pdf'.format(self.main_invoice_data.get('invoice_id'))
                	filename = '/home/ubuntu/amcrest_gps_pro/user/invoices/invoice_{}.pdf'.format(self.main_invoice_data.get('invoice_id'))
                	encoded_string = ''
                	if self.category=='obd':
                		html_string = render_to_string('invoice_obd.html', self.main_invoice_data)
                		html = HTML(string=html_string)
	                	html.write_pdf(target=filename)
                	else:
                		html_string = render_to_string('invoice.html', self.main_invoice_data)
	                	html = HTML(string=html_string)
	                	html.write_pdf(target=filename)

	                with open(filename, "rb") as pdf_file:
	                	encoded_string = base64.b64encode(pdf_file.read())
	                os.remove(filename)
            return JsonResponse({'message':'Invoice Generated Successfully', 'status':True, 'status_code':200, 'invoice':encoded_string.decode('utf-8')}, status=200)
        return JsonResponse({'message':'Bad Request, Email Required', 'status_code':200, 'status':False}, status=200)


    def get_subscription_details(self, sub_id):
        
        subscription_obj = {}
        if sub_id:
            try:
                subscription = gateway.subscription.find(sub_id)
                subscription_obj['timestamp'] = subscription.status_history[0].timestamp
                subscription_obj['status'] = subscription.status_history[0].status
                subscription_obj['billing_period_end_date'] = str(subscription.billing_period_end_date.month)+'/'+str(subscription.billing_period_end_date.day)+'/'+str(subscription.billing_period_end_date.year)
                subscription_obj['billing_period_start_date'] = str(subscription.billing_period_start_date.month)+'/'+str(subscription.billing_period_start_date.day)+'/'+str(subscription.billing_period_start_date.year)
                subscription_obj['next_billing_date'] = str(subscription.next_billing_date.month)+'/'+str(subscription.next_billing_date.day)+'/'+str(subscription.next_billing_date.year)
                subscription_obj['plan'] = self.get_plan_desc(subscription.plan_id)
            except(Exception)as e:
                print(e)
                pass
        else:
            subscription_obj['timestamp'] = subscription.status_history[0].timestamp
            subscription_obj['status'] = subscription.status_history[0].status
            subscription_obj['billing_period_end_date'] = str(subscription.billing_period_end_date.month)+'/'+str(subscription.billing_period_end_date.day)+'/'+str(subscription.billing_period_end_date.year)
            subscription_obj['billing_period_start_date'] = str(subscription.billing_period_start_date.month)+'/'+str(subscription.billing_period_start_date.day)+'/'+str(subscription.billing_period_start_date.year)
            subscription_obj['next_billing_date'] = str(subscription.next_billing_date.month)+'/'+str(subscription.next_billing_date.day)+'/'+str(subscription.next_billing_date.year)
            subscription_obj['plan'] = 'Manual Charge'
        return subscription_obj

    def get_plan_desc(self, plan_id):
    	if self.category == 'gps':
    		subscription_plan = ServicePlan.objects.filter(service_plan_id=plan_id).first()
    		if subscription_plan:
    			return subscription_plan.service_plan_name
    		return 'Amcrest GPS Pro Service'
    	else:
    		subscription_plan = ServicePlanObd.objects.filter(service_plan_id=plan_id).first()
    		if subscription_plan:
    			return subscription_plan.service_plan_name
    		return 'Amcrest GPS Fleet Service'