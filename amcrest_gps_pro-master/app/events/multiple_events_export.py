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
import base64


from app.serializers import *
from app.models import *


from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration



class ExportMultipleEventListIndivdualDate(APIView):
	# permission_classes = (AllowAny,)
	def post(self, request):
		request_from_date = request.data.get('from', None)
		request_to_date = request.data.get('to', None)
		request_date = request.data.get('date', None)
		event = request.data.get('events', None)
		imei = request.data.get('imei', None)
		customer_id = request.data.get('customer_id', None)
		ascending = request.data.get('ascending', True)

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')
			try:

				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")

				# print(record_date_gte, record_date_lte)

				if 'notification' in event:
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all().order_by("record_date_timezone")
				else:
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id, type__in=event).all().order_by("record_date_timezone")

				# print(notifications)
				serializer = NotificationsReadSerializer(notifications, many=True)
				close_old_connections()
				encoded_string = self.generate_file(serializer.data, customer_id)
				return JsonResponse({'message':'Event list', 'from_date':request_from_date, 'to_date':request_to_date, 'file':encoded_string.decode('utf-8'), 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				print(e)
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				
				if 'notification' in event:
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all().order_by("record_date_timezone")
				else:
					notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id, type__in=event).all().order_by("record_date_timezone")
					
				serializer = NotificationsReadSerializer(notifications, many=True)
				close_old_connections()
				encoded_string = self.generate_file(serializer.data, customer_id)
				return JsonResponse({'message':'Event list', 'from_date':request_date, 'to_date':request_date, 'file':encoded_string.decode('utf-8'), 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				print(e)
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_date, 'to_date':request_date}, status=200)
		close_old_connections()
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'notifications':[]}, status=200)



	def generate_file(self, rows, customer_id):
		if customer_id:
			if rows:
				new_rows = []
				count = 1
				for i in rows:
					i['count'] = count
					count = count + 1
					new_rows.append(i)
				rows = new_rows

			filename = 'report_export_{}.pdf'.format(str(customer_id))
			encoded_string = ''
			font_config = FontConfiguration()
			html_string = render_to_string('report_export.html',
				{'data': rows})
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
			html.write_pdf(target=filename, stylesheets=[css], font_config=font_config)
			with open(filename, 'rb') as pdf_file:
				encoded_string = base64.b64encode(pdf_file.read())
				os.remove(filename)
			return encoded_string