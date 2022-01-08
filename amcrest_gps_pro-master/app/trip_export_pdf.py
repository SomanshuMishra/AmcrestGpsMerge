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
import pandas as pd


from app.serializers import *
from app.models import *


from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

trip_columns = {
    "trip_number":"Trip No.",
    "started_at" : "Started At",
    "ended_at" : "Ended At",
    "distance" : "Distance ({})",
    "duration" : "Duration",
    "from" : "From",
    "to" : "To"
}



class TripExportApiView(APIView):

    # permission_classes = (AllowAny, )

    def post(self, request):
        rows = request.data.get('data', None)
        unit = request.data.get('unit', 'Miles')
        customer_id = request.data.get('customer_id', None)
        _type = request.data.get('type', 'csv')
        category = request.GET.get('category', 'gps')
        if customer_id:
            if rows:
                new_rows = []
                count = 1
                for i in rows:
                    i['count'] = count
                    count = count + 1
                    new_rows.append(i)
                rows = new_rows

            if _type == 'pdf':
                filename = 'trip_export_{}.pdf'.format(str(customer_id))
                encoded_string = ''
                font_config = FontConfiguration()

                if category == 'gps':
                    html_string = render_to_string('trip_export.html',
                            {'data': rows, 'unit': unit})
                else:
                    html_string = render_to_string('trip_export_obd.html',
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

                filename = 'trip_export_'+str(customer_id)+'.csv'
                data_frame.to_csv(filename, index=False)

            with open(filename, 'rb') as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read())
                os.remove(filename)
            return JsonResponse({
                'message': 'Trips Exported',
                'status': True,
                'status_code': 200,
                'encoded_string': encoded_string.decode('utf-8'),
                }, status=200)
        return JsonResponse({'message': 'Customer ID required',
                                'status': False, 'status_code': 400},
                                status=200)