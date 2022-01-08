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
    "title": "Title",
	"body": "Body",
	"record_date_timezone": "Date Time"
}



class ReportExportApiView(APIView):
    # permission_classes = (AllowAny, )
    def post(self, request):
        rows = request.data.get('data', None)
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
                filename = 'notification_export_{}.pdf'.format(str(customer_id))
                encoded_string = ''
                font_config = FontConfiguration()
                html_string = render_to_string('notification_export_obd.html',
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

                html.write_pdf(target=filename, stylesheets=[css],
                               font_config=font_config)
            else:
                data_frame = pd.DataFrame(rows)
                data_frame = data_frame.rename(index=str, columns=trip_columns)

                filename = 'notification_export_'+str(customer_id)+'.csv'
                data_frame.to_csv(filename, index=False)

            with open(filename, 'rb') as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                # os.remove(filename)
            return JsonResponse({
                'message': 'Notification Exported',
                'status': True,
                'status_code': 200,
                'encoded_string': encoded_string.decode('utf-8'),
                }, status=200)
        return JsonResponse({'message': 'Customer ID required',
                                'status': False, 'status_code': 400},
                                status=200)



# import events_notifications


class NotificationView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei):
		request_from_date = request.GET.get('from', None)
		request_to_date = request.GET.get('to', None)
		request_date = request.GET.get('date', None)

		if request_from_date and request_to_date:
			from_date = request_from_date.split('-')
			to_date = request_to_date.split('-')
			try:
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all().order_by("record_date_timezone")
				serializer = NotificationsReadSerializer(notifications, many=True)
				close_old_connections()
				return JsonResponse({'message':'Notification list', 'from_date':request_from_date, 'to_date':request_to_date, 'notifications':serializer.data, 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_from_date, 'to_date':request_to_date}, status=200)
		elif request_date:
			try:
				from_date = request_date.split('-')
				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id).all().order_by("record_date_timezone")
				serializer = NotificationsReadSerializer(notifications, many=True)
				close_old_connections()
				return JsonResponse({'message':'Notification list', 'from_date':request_date, 'to_date':request_date, 'notifications':serializer.data, 'status':True, 'status_code':200}, status=200)
			except(Exception)as e:
				close_old_connections()
				return JsonResponse({'message':'Invalid Date Format or IMEI, Please check', 'status':False, 'status_code':400, 'from_date':request_date, 'to_date':request_date}, status=200)
		return JsonResponse({'message':'Invalid Query, From date and To date or else Date required in query', 'status':False, 'status_code':400, 'notifications':[]}, status=200)



# class ZoneNotificationView(APIView):
# 	def get(self, request, customer_id, imei):
# 		request_from_date = request.GET.get('from', None)
# 		request_to_date = request.GET.get('to', None)
# 		request_date = request.GET.get('date', None)

# 		if request_from_date and request_to_date:
# 			from_date = request_from_date.split('-')
# 			to_get = request_to_date.split('-')

# 			try:
# 				record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")
# 				record_date_lte = datetime.datetime.strptime(to_date[2]+"-"+to_date[1]+"-"+to_date[0]+" 23:59:59", "%Y-%m-%d %H:%M:%S")
# 				notifications = Notifications.objects.filter(record_date_timezone__gte = record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=customer_id, eve)


class DeleteNotificationView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, id):
		if id:
			notification = Notifications.objects.filter(id=id).first()
			if notification:
				notification.delete()
		return JsonResponse({'message':'Report Deleted Successfully', 'status':True, 'status_code':200}, status=200)