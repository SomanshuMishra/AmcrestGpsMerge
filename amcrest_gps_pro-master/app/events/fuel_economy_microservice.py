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

from listener.models import *
from listener.serializers import *

from .location_finder import *
from .voltage import voltage_event_module

from django.contrib.auth import get_user_model
User = get_user_model()


time_fmt = '%H:%M:%S'
date_fmt = '%Y-%m-%d'
date_time_fmt = '%Y-%m-%d %H:%M:%S'



from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.template import Context
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


trip_columns = {
    "trip_number":"No.",
    "imei" : "IMEI",
    "fuel_economy" : "Fuel Economy ({})",
    "date" : "Date"
}



class EconomyExportApiView(APIView):
    # permission_classes = (AllowAny, )
    def post(self, request):
        rows = request.data.get('data', None)
        unit = request.data.get('unit', 'KM')
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
                filename = 'economy_export_{}.pdf'.format(str(customer_id))
                encoded_string = ''
                font_config = FontConfiguration()
                html_string = render_to_string('economy_export.html',
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
                trip_columns['fuel_economy'] = trip_columns['fuel_economy'].format(unit) 
                data_frame = pd.DataFrame(rows)
                data_frame = data_frame.rename(index=str, columns=trip_columns)

                filename = 'economy_export_'+str(customer_id)+'.csv'
                data_frame.to_csv(filename, index=False)

            with open(filename, 'rb') as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                os.remove(filename)
            return JsonResponse({
                'message': 'Economy Exported',
                'status': True,
                'status_code': 200,
                'encoded_string': encoded_string.decode('utf-8'),
                }, status=200)
        return JsonResponse({'message': 'Customer ID required',
                                'status': False, 'status_code': 400},
                                status=200)



class FuelEconomyMicroService(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		dates = request.data.get('dates', None)
		imei = request.data.get('imei', None)
		model = request.data.get('model', None)
		fuel_economy_list = []
		if imei and model:
			if dates:
				for date in dates:
					date_split = date.split('-')
					fuel = FuelEconomy.objects.filter(imei=imei, record_date__day=date_split[0], record_date__month=date_split[1], record_date__year=date_split[2], fuel_economy__isnull=False).last()
					
					economy = {}
					economy['date'] = date
					economy['imei'] = imei
					if fuel:
						economy['fuel_economy'] = fuel.fuel_economy
					else:
						economy['fuel_economy'] = None
						
					if economy['fuel_economy']:
						fuel_economy_list.append(economy)
				return JsonResponse({'message':'Fuel Economy', 'status':True, 'status_code':200, 'fuel_economy':fuel_economy_list}, status=200)
			return JsonResponse({'message':'Atleast one date required', 'status':True, 'status_code':200, 'fuel_economy':[]}, status=200)
		return JsonResponse({'message':'IMEI, Device Model and Dates required', 'status':False, 'status_code':400, 'fuel_economy':[]}, status=200)



class FuelConsumptionMicroService(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		dates = request.data.get('dates', None)
		imei = request.data.get('imei', None)
		fuel_economy_list = []
		if imei:
			if dates:
				for date in dates:
					date_split = date.split('-')
					fuel = FuelConsumption.objects.filter(imei=imei, record_date__day=date_split[0], record_date__month=date_split[1], record_date__year=date_split[2], consumption__isnull=False).last()
					
					economy = {}
					economy['date'] = date
					economy['imei'] = imei
					if fuel:
						economy['consumption'] = fuel.consumption
					else:
						economy['consumption'] = None
						
					if economy['consumption']:
						fuel_economy_list.append(economy)
				return JsonResponse({'message':'Fuel consumption', 'status':True, 'status_code':200, 'fuel_consumption':fuel_economy_list}, status=200)
			return JsonResponse({'message':'Atleast one date required', 'status':True, 'status_code':200, 'fuel_economy':[]}, status=200)
		return JsonResponse({'message':'IMEI, Device Model and Dates required', 'status':False, 'status_code':400, 'fuel_economy':[]}, status=200)



class ManualGenerateFuelEconomy(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.imei = None
		self.day = None
		self.month = None
		self.year = None

	def post(self, request):
		self.imei = request.data.get('imei', None)
		date = request.data.get('date', None)
		dates = date.split('-')
		if self.imei and date:
			sim_mapping = SimMapping.objects.filter(imei=self.imei).last()
			if sim_mapping:
				if sim_mapping.category == 'obd':
					print(sim_mapping.model)
					if sim_mapping.model == 'GV500' or sim_mapping.model == 'gv500':
						fuel_eco = FuelEconomyManualGenerate(self.imei, dates[0], dates[1], dates[2])
						fuel_eco.generate()
					elif sim_mapping.model == 'topfly' or sim_mapping.model == 'TOPFLY':
						record_date_gte = datetime.datetime.strptime(dates[2]+"-"+dates[1]+"-"+dates[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
						record_date_lte = datetime.datetime.strptime(dates[2]+"-"+dates[1]+"-"+dates[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
						user_trip = UserObdTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=self.imei).first()
						if user_trip:
							fuel_eco = FuelEventsMachine(user_trip.id)
							fuel_eco.generate()
					return JsonResponse({'message':'Fuel Economy Generated Successfully', 'status':True, 'status_code':200}, status=200)
				return JsonResponse({'message':'Invalid IMEI, cannot generate fuel economy', 'status':False, 'status_code':200}, status=200)
			return JsonResponse({'message':'Invalid IMEI, cannot generate fuel economy', 'status':False, 'status_code':200}, status=200)
		return JsonResponse({'message':'Invalid request, IMEI and Date required', 'status':False, 'status_code':400}, status=200)


class FuelEventsMachine:
	def __init__(self, trip_id):
		self.trip_id = trip_id
		self.imei = None

	def generate(self):
		try:
			trip = UserObdTrip.objects.filter(id=self.trip_id).first()
		except(Exception)as e:
			trip = None

		self.imei = trip.imei
		economy = None

		if trip and self.trip_id:
			try:
				trip_logs = trip.trip_log
			except(Exception)as e:
				trip_logs = None

			
			start_trip_log = trip_logs[0]
			end_trip_log = trip_logs[-1]

			if start_trip_log[0].get('fuel_consumption'):
				start_fuel = start_trip_log[0].get('fuel_consumption')
			else:
				start_fuel = start_trip_log[1].get('fuel_consumption')


			if end_trip_log[-1].get('fuel_consumption'):
				end_fuel = end_trip_log[-1].get('fuel_consumption')
			else:
				end_fuel = end_trip_log[-2].get('fuel_consumption1')


			if start_trip_log[0].get('mileage'):
				start_mileage = start_trip_log[0].get('mileage')
			else:
				start_mileage = start_trip_log[1].get('mileage')


			if end_trip_log[-1].get('mileage'):
				end_mileage = end_trip_log[-1].get('mileage')
			else:
				end_mileage = end_trip_log[-2].get('mileage')

			try:
				fuel_consumed = (float(end_fuel) - float(start_fuel))
			except(Exception)as e:
				fuel_consumed = 0

			try:
				fuel_consumed = fuel_consumed/3785.412
			except(Exception)as e:
				fuel_consumed = fuel_consumed


			try:
				mileage = float(end_mileage) - float(start_mileage)
			except(Exception)as e:
				mileage = 0

			try:
				hd = (1/fuel_consumed)*mileage
				economy = (1/0.264172)*hd
			except(Exception)as e:
				economy = 0

			try:
				fuel_event = FuelEconomy.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)

			customer_id = self.get_customer_id(self.imei)
			voltage_obj = {
				'imei': self.imei,
				'fuel_economy': economy,
				'record_date':trip.record_date_timezone.date(),
				'customer_id':customer_id
			}

			serializer = FuelEconomySerializer(data=voltage_obj)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()


			try:
				fuel_event = FuelConsumption.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)

			fuel_consumption_obj = {
				'imei':self.imei,
				'consumption':fuel_consumed,
				'record_date': trip.record_date_timezone.date(),
				'customer_id':customer_id
			}
			serializer = FuelConsumptionSerializer(data=fuel_consumption_obj)
			if serializer.is_valid():
				serializer.save()

		return economy


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


class FuelEconomyManualGenerate:
	def __init__(self, imei, day, month, year):
		self.imei = imei
		self.day = day
		self.month = month
		self.year = year
		self.fuel_capacity = self.get_fuel_capacity(imei)


	def generate(self):
		timezone = self.get_time_zone(self.imei)
		fuel_economy_list = []
		fuel_emission_list = []
		final_fuel_economy = None
		if timezone:
			time_to_start, time_to_end = self.get_date_to_filter(timezone, self.day,self. month, self.year)
			data = self.get_data(self.imei, time_to_start, time_to_end)
			
			if self.fuel_capacity:
				for d in data:
					if d.get('journey_fuel_consumption') and d.get('trip_mileage'):
						fuel_capacity_per = (float(d.get('journey_fuel_consumption'))/100)*self.fuel_capacity
						fuel_economy_per_km = 1/fuel_capacity_per
						fuel_economy_list.append(d.get('trip_mileage')*fuel_economy_per_km)
						fuel_emission_list.append(fuel_capacity_per)

				print(fuel_economy_list)
				print(fuel_emission_list)

			if fuel_economy_list:
				final_fuel_economy = sum(fuel_economy_list)/len(fuel_economy_list)
				self.save_fuel_economy(self.imei, time_to_start.date(), final_fuel_economy)

			if fuel_emission_list:
				self.save_fuel_emission(self.imei, time_to_start.date(), fuel_emission_list)


			if fuel_emission_list:
				self.save_fuel_consumption(self.imei, time_to_start.date(), fuel_emission_list)

		return final_fuel_economy


	def save_fuel_economy(self, imei, date, fuel_economy):
		if fuel_economy:
			if fuel_economy>0:
				fuel_event = FuelEconomy.objects.filter(imei=imei, record_date=date).all()
				if fuel_event:
					fuel_event.delete()
				voltage_obj = {
					'imei': imei,
					'fuel_economy': fuel_economy,
					'record_date':date,
					'customer_id':self.customer_id
				}

				serializer = FuelEconomySerializer(data=voltage_obj)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
		pass


	def save_fuel_consumption(self, imei, date, fuel_economy):
		if fuel_economy:
			if fuel_economy>0:
				fuel_event = FuelConsumption.objects.filter(imei=imei, record_date=date).all()
				if fuel_event:
					fuel_event.delete()
					

				fuel_consumption_obj = {
					'imei':imei,
					'consumption':sum(fuel_economy),
					'record_date': date,
					'customer_id':self.customer_id
				}
				serializer = FuelConsumptionSerializer(data=fuel_consumption_obj)
				if serializer.is_valid():
					serializer.save()
		pass

	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			self.customer_id = sub.customer_id
			try:
				user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
				if user:
					return user.time_zone
			except(Exception)as e:
				print(e)
				return None
		return None


	def save_fuel_emission(self, imei, date, emission):
		if emission:
			if emission>0:
				emission_obj = Emission.objects.filter(imei=imei, record_date=date).all()
				if emission_obj:
					emission_obj.delete()

				economy = sum(emission)*8.8
				voltage_obj = {
					'imei': imei,
					'emission': economy,
					'record_date':date,
					'customer_id':self.customer_id
				}
				serializer = EmissionSerializer(data=voltage_obj)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
		pass


	def get_data(self, imei, time_date_start, time_date_end):
		try:
			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()
		except(Exception)as e:
			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()

		stt_serializer = EngineSummarySerializer(stt, many=True).data
		data = [dict(i) for i in stt_serializer]
		records = sorted(data, key = lambda i: i['send_time'],reverse=False)
		return records

	def get_fuel_capacity(self, imei):
		fuel = SettingsModel.objects.filter(imei=imei).last()
		if fuel:
			if fuel.fuel_capacity:
				return fuel.fuel_capacity
			return None
		return None


	def get_date_to_filter(self, timezone, day, month, year):
		timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', date_time_fmt)
		old_timezone = pytz.timezone(timezone)

		new_timezone = pytz.timezone("UTC")
		my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
		timestamp_end = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', date_time_fmt)
		old_timezone_end = pytz.timezone(timezone)
		new_timezone_end = pytz.timezone("UTC")
		my_timestamp_in_new_timezone_end = old_timezone_end.localize(timestamp_end).astimezone(new_timezone_end)
		return my_timestamp_in_new_timezone, my_timestamp_in_new_timezone_end