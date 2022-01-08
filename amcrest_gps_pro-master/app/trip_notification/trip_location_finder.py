from geopy.geocoders import Nominatim
from django.conf import settings
from django.db import close_old_connections
from app.models import *
from app.serializers import *
import json
import requests

from app.events import main_location_machine

from services.models import *
def get_amcrest_location_key():
	key = AppConfiguration.objects.filter(key_name='noti_key').last()
	if key:
		return key.key_value
	return '2di4d2dd'
	
def get_google_keys():
	google_key = GoogleMapAPIKey.objects.first()
	close_old_connections()
	if google_key:
		return str(google_key.key)
	return str(settings.GOOGLE_MAP_KEY)

def get_location(longitude, latitude):
	check_location = requests.get('https://amcrestgpstracker.com/manage_gps/fetchlocation_noti.php?lat='+str(latitude)+'&long='+str(longitude)+'&noti_key='+get_amcrest_location_key())
	if check_location.text != 'NONE' or check_location.text != '':
		
		return str(check_location.text)
	else:
		try:
			response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(latitude)+","+str(longitude)+"&key="+get_google_keys())
			location_to_send = json.loads(response.text)
		except(Exception)as e:
			return 'Unknown'
			
		try:
			location_to_send = location_to_send.get('results', None)[0]
			location_to_send = location_to_send.get('formatted_address', None)
		except(Exception)as e:
			location_to_send = None

		if location_to_send:
			return location_to_send
		else:
			return 'Unknown'