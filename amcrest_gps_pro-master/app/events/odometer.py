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
import datetime

from app.serializers import *
from app.models import *

import os
import base64
import pandas as pd

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.template import Context
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


trip_columns = {
    "imei" : "IMEI",
    "distance" : "Distance ({})",
    "record_date" : "Date"
}



class OdometerExportApiView(APIView):
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
                filename = 'odometer_export_{}.pdf'.format(str(customer_id))
                encoded_string = ''
                font_config = FontConfiguration()
                html_string = render_to_string('odometer_export.html',
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
                trip_columns['distance'] = trip_columns['distance'].format(unit) 
                data_frame = pd.DataFrame(rows)
                data_frame = data_frame.rename(index=str, columns=trip_columns)

                filename = 'odometer_export_'+str(customer_id)+'.csv'
                data_frame.to_csv(filename, index=False)

            with open(filename, 'rb') as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                os.remove(filename)
            return JsonResponse({
                'message': 'Odometer Exported',
                'status': True,
                'status_code': 200,
                'encoded_string': encoded_string.decode('utf-8'),
                }, status=200)
        return JsonResponse({'message': 'Customer ID required',
                                'status': False, 'status_code': 400},
                                status=200)



def odometere_event_module(args):
	trip_id = args[0]
	fuel_event = OdometerEventMachine(trip_id)
	fuel_event.odometer_event()


class OdometerEventMachine:
	def __init__(self, trip_id):
		self.trip_id = trip_id
		self.imei = None
		self.distance = []

	def odometer_event(self):

		try:
			trip = UserObdTrip.objects.filter(id=self.trip_id).first()
		except(Exception)as e:
			print(e, '0000000000')
			trip = None

		self.imei = trip.imei
		self.get_total_distance_travelled(trip.measure_id)

		try:
			odometer_instance = Odometere.objects.filter(imei=self.imei, record_date_timezone=trip.record_date_timezone.date()).all()
			if odometer_instance:
				odometer_instance.delete()
		except(Exception)as e:
			print(e)
			pass

		try:
			odometer_object = {
				"imei": self.imei,
				"distance": sum(self.distance),
				"record_date_timezone": trip.record_date_timezone.date(),
				"customer_id":self.get_customer_id()
			}
		except(Exception)as e:
			print(e)
			odometer_object = {}

		serializer = OdometereSerializer(data=odometer_object)
		if serializer.is_valid():
			serializer.save()
		else:
			print(serializer.errors)


	def get_total_distance_travelled(self, measure_id):
		mes = TripsObdMesurement.objects.filter(measure_id=measure_id).first()
		if mes:
			self.distance = mes.total_distance
		else:
			self.distance = [0]


	def get_customer_id(self):
		customer_id = Subscription.objects.filter(imei_no=self.imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None


class OdometerView(APIView):
	permission_classes = (AllowAny,)
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
				odometer_instance = Odometere.objects.filter(imei=imei, record_date_timezone__range=[filter_from_date, filter_to_date], customer_id=customer_id).all()
				
				serializer = OdometereSerializer(odometer_instance, many=True)
				close_old_connections()
				return JsonResponse({'message':'Odometere details', 'from_date':request_from_date, 'to_date':request_to_date, 'odometere':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				odometer_instance = Odometere.objects.filter(imei=imei, record_date_timezone__day=from_date[0], record_date_timezone__month=from_date[1], record_date_timezone__year=from_date[2], customer_id=customer_id).first()
				serializer = OdometereSerializer(odometer_instance)
				close_old_connections()
				return JsonResponse({'message':'Odometere details', 'date':request_date, 'odometere':serializer.data, 'status_code':200, 'status':True}, status=200)
			except(Exception)as e:
				return JsonResponse({'message':'Invalid Date Format, Please check', 'status':False, 'status_code':400, 'date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'odometere':[]}, status=200)