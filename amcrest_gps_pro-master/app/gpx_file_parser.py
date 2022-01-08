from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate
from django.conf import settings
from geopy.geocoders import Nominatim

import xml.etree.ElementTree as ET

from django.core.files.storage import default_storage

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q as queue

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import datetime

import os

import gpx_parser as parser
from xml.etree import ElementTree as ET
from lxml import etree

import gpxpy
import gpxpy.gpx


class GpxFileParserView(APIView):
	# permission_classes = (AllowAny,)
	parser_classes = (MultiPartParser,JSONParser,)
	def post(self, request):
		file = request.FILES.get('file')
		file_name = default_storage.save(file.name, file)
		file = default_storage.open(file_name)
		file_url = default_storage.url(file_name)
		SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
		locations = []
		with open(settings.BASE_DIR+file_url, 'r') as gpx_file:
			# gpx = parser.parse(gpx_file)
			gpx = gpxpy.parse(gpx_file)

			for track in gpx.tracks:
				for segment in track.segments:
					for point in segment.points:
						location_obj = {
							'latitude':point.latitude,
							'longitude':point.longitude
						}
						locations.append(location_obj)

			if not locations:
				for waypoint in gpx.waypoints:
					location_obj = {
								'latitude':waypoint.latitude,
								'longitude':waypoint.longitude,
								'waypoint_name' : waypoint.name
							}
					locations.append(location_obj)

			if not locations:
				for route in gpx.routes:
				    for point in route.points:
				    	location_obj = {
				    		'latitude':point.latitude,
				    		'longitude':point.longitude,
				    		'elevation' : point.elevation
				    	}
				    	locations.append(location_obj)
		os.remove(settings.BASE_DIR+file_url)
		return JsonResponse({'message':'File Reading', 'status':True, 'status_code':200, 'locations':locations}, status=200)