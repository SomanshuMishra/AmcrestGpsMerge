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

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import json
import datetime
import time
import pytz
import _thread

import asyncio
import hashlib
import os
import base64
import pandas as pd


from app.serializers import *
from app.models import *

from services.models import *

from .location_finder import *
from .voltage import voltage_event_module

from django.contrib.auth import get_user_model
User = get_user_model()

time_fmt = '%H:%M:%S'
date_fmt = '%Y-%m-%d'
date_time_fmt = '%Y-%m-%d %H:%M:%S'



class EmissionView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei):
		request_from_date = request.GET.get('from', None)
		request_to_date = request.GET.get('to', None)
		request_date = request.GET.get('date', None)

		if request_from_date and request_to_date:
			try:
				from_date = request_from_date.split('-')
				to_date = request_to_date.split('-')

				filter_from_date = from_date[2]+"-"+from_date[1]+"-"+from_date[0]
				filter_to_date = to_date[2]+"-"+to_date[1]+"-"+to_date[0]
				emission_instance = Emission.objects.filter(imei=imei, record_date__range=[filter_from_date, filter_to_date], customer_id=customer_id).all()
				serializer = EmissionSerializer(emission_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Emission details', 'from_date':request_from_date, 'to_date':request_to_date, 'emission':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				emission_instance = Emission.objects.filter(imei=imei, record_date__day=from_date[0], record_date__month=from_date[1], record_date__year=from_date[2], customer_id=customer_id).first()
				serializer = EmissionSerializer(emission_instance)
				close_old_connections()
				return JsonResponse({'message':'Emission details', 'date':request_date, 'emission':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				print(e)
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'emission':[]}, status=200)


from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.template import Context
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


trip_columns = {
    "trip_number":"No.",
    "imei" : "IMEI",
    "emission" : "Emission ({})",
    "date" : "Date"
}



class EmissionExportApiView(APIView):
    # permission_classes = (AllowAny, )
    def post(self, request):
        rows = request.data.get('data', None)
        unit = request.data.get('unit', 'Lb/Gallon')
        customer_id = request.data.get('customer_id', None)
        _type = request.data.get('type', 'csv')
        if customer_id:
            # if rows:
            #     new_rows = []
            #     count = 1
            #     for i in rows:
            #         i['count'] = count
            #         count = count + 1
            #         new_rows.append(i)
            #     rows = new_rows

            if _type == 'pdf':
                filename = 'emission_export_{}.pdf'.format(str(customer_id))
                encoded_string = ''
                font_config = FontConfiguration()
                html_string = render_to_string('emmission_export.html',
                        {'data': rows, 'unit': unit})
                html = HTML(string=html_string)
                css = \
                    CSS(string='''
    	        			@page { size: A4; margin: 1cm }
    					    @font-face {
    					        font-family: Gentium;
    					        src: url(http://example.com/fonts/Gentium.otf);
    					    }
    					    h1 { font-family: Gentium }
    					    img{
    					    	height:20px;
    					    }''',
                        font_config=font_config)

                html.write_pdf(target=filename, stylesheets=[css],
                               font_config=font_config)
            else:
                trip_columns['emission'] = trip_columns['emission'].format(unit) 
                data_frame = pd.DataFrame(rows)
                data_frame = data_frame.rename(index=str, columns=trip_columns)

                filename = 'emission_export_'+str(customer_id)+'.csv'
                data_frame.to_csv(filename, index=False)

            with open(filename, 'rb') as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                os.remove(filename)
            return JsonResponse({
                'message': 'Emission Exported',
                'status': True,
                'status_code': 200,
                'encoded_string': encoded_string.decode('utf-8'),
                }, status=200)
        return JsonResponse({'message': 'Customer ID required',
                                'status': False, 'status_code': 400},
                                status=200)





def fuel_emission_module(args):
	trip_id = args[0]
	sim_mapping = SimMapping.objects.filter(imei=args[1]).last()
	if sim_mapping.model == 'topfly' or sim_mapping.model == 'TOPFLY':
		fuel_event = EmissionMachine(trip_id)
		fuel_event.receive_trip_event()


class EmissionMachine:
	def __init__(self, trip_id):
		self.trip_id = trip_id
		self.imei = None

	def receive_trip_event(self):
		try:
			trip = UserObdTrip.objects.filter(id=self.trip_id).first()
		except(Exception)as e:
			trip = None
		self.imei = trip.imei

		if trip and self.trip_id:
			try:
				trip_logs = trip.trip_log
			except(Exception)as e:
				trip_logs = None

			try:
				fuel_event = Emission.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)

			start_trip_log = trip_logs[0]
			end_trip_log = trip_logs[-1]

			if start_trip_log[0].get('fuel_consumption'):
				start_fuel = start_trip_log[0].get('fuel_consumption')
			else:
				start_fuel = start_trip_log[1].get('fuel_consumption')


			if end_trip_log[-1].get('fuel_consumption'):
				end_fuel = end_trip_log[-1].get('fuel_consumption')
			else:
				end_fuel = end_trip_log[-2].get('fuel_consumption')

			try:
				fuel_consumed = float(end_fuel) - float(start_fuel)
			except(Exception)as e:
				fuel_consumed = 0

			try:
				fuel_consumed = fuel_consumed/3785.412
			except(Exception)as e:
				fuel_consumed = fuel_consumed

			try:
				economy = fuel_consumed*8.8
			except(Exception)as e:
				economy = 0

			customer_id = self.get_customer_id(self.imei)
			voltage_obj = {
				'imei': self.imei,
				'emission': economy,
				'record_date':trip.record_date_timezone.date(),
				'customer_id':customer_id
			}
			# print(voltage_obj)
			serializer = EmissionSerializer(data=voltage_obj)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()


	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None

	def format_date(self, date):
		date_time = datetime.datetime.strptime(date[:4]+'-'+date[4:6]+'-'+date[6:8]+' '+date[-6:-4]+':'+date[-4:-2]+':'+date[-2:], date_time_fmt)
		time_zone = self.get_time_zone(self.imei)
		date_time = date_time.astimezone(pytz.timezone(time_zone))
		return date_time

	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
			close_old_connections()
			if user:
				return user.time_zone
		close_old_connections()
		return 'UTC'

	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None