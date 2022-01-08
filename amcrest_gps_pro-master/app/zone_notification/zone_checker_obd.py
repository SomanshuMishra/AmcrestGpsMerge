from django.conf import settings
import asyncio

from .zone_notification_sender import send_notification
from .zone_location_finder import get_location
from .zone_notification_maker import *

from app.models import Subscription, SettingsModel, Zones, ZoneAlert
import _thread

from django.conf import settings
from django.db import close_old_connections
import asyncio




def zone_checker(imei, details):
	_thread.start_new_thread(check_no_go_zone, (imei, details))
	_thread.start_new_thread(check_keep_in_zone, (imei, details))
	_thread.start_new_thread(check_both_zone, (imei, details))
	pass

def check_both_zone(imei, details):
	subscription = Subscription.objects.filter(imei_no=imei).last()
	if subscription:
		zones = ZoneAlert.objects.filter(customer_id=subscription.customer_id, zone__type='both', imei=imei).all()
		if zones:
			for zone in zones:
				lng = details.get('longitude')
				lat = details.get('latitude')
				speed = details.get('speed')
				coordinates = eval(str(zone.zone.coordinates_tuple))
				if coordinates:
					_thread.start_new_thread(check_device_no_go_zone, (imei, lat, lng, coordinates, zone.name, speed, zone.zone.id, zone.id, details))
					_thread.start_new_thread(check_device_keep_in_zone, (imei, lat, lng, coordinates, zone.name, speed, zone.zone.id, zone.id, details))
	close_old_connections()
	pass


def check_no_go_zone(imei, details):
	subscription = Subscription.objects.filter(imei_no=imei).last()
	if subscription:
		zones = ZoneAlert.objects.filter(customer_id=subscription.customer_id, zone__type='no-go', imei=imei).all()
		
		if zones:
			for zone in zones:
				lng = details.get('longitude')
				lat = details.get('latitude')
				speed = details.get('speed')
				coordinates = eval(str(zone.zone.coordinates_tuple))
				if coordinates:
					_thread.start_new_thread(check_device_no_go_zone, (imei, lat, lng, coordinates, zone.name, speed, zone.zone.id, zone.id, details))
	close_old_connections()
	pass


def check_device_no_go_zone(imei, latitude, longitude, coordinates, alert_name, speed, zone, zone_alert, details):
	n = len(coordinates)
	try:
		x = float(latitude)
	except(Exception)as e:
		x = None

	try:
		y = float(longitude)
	except(Exception)as e:
		y = None

	if x and y:
		inside = False
		p1x, p1y = coordinates[0]
		for i in range(1, n + 1):
			p2x, p2y = coordinates[i % n]
			if y > min(p1y, p2y):
				if y <= max(p1y, p2y):
					if x <= max(p1x, p2x):
						if p1y != p2y:
							xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
						if p1x == p2x or x <= xinters:
							inside = not inside
			p1x, p1y = p2x, p2y
		if inside:
			args = [imei, latitude, longitude, alert_name, speed, zone, zone_alert, details]
			try:
				loop = asyncio.new_event_loop()
				loop.run_in_executor(None, device_no_go_notification_sender, args)
			except(Exception)as e:
				pass
		else:
			args = [imei, latitude, longitude, alert_name, speed, zone, zone_alert, details]
			try:
				loop = asyncio.new_event_loop()
				loop.run_in_executor(None, device_out_no_go_notification_sender, args)
			except(Exception)as e:
				pass
	



def check_keep_in_zone(imei, details):
	subscription = Subscription.objects.filter(imei_no=imei).last()
	if subscription:
		zones = ZoneAlert.objects.filter(customer_id=subscription.customer_id, zone__type='keep-in', imei=imei).all()
		if zones:
			for zone in zones:
				lng = details.get('longitude')
				lat = details.get('latitude')
				speed = details.get('speed')
				coordinates = eval(str(zone.zone.coordinates_tuple))
				if coordinates:
					_thread.start_new_thread(check_device_keep_in_zone, (imei, lat, lng, coordinates, zone.name, speed, zone.zone.id, zone.id, details))
	close_old_connections()
	pass


def check_device_keep_in_zone(imei, latitude, longitude, coordinates, alert_name, speed, zone, zone_alert, details):
	n = len(coordinates)
	try:
		x = float(latitude)
	except(Exception)as e:
		x = None

	try:
		y = float(longitude)
	except(Exception)as e:
		y = None

	if x and y:
		inside = False
		p1x, p1y = coordinates[0]
		for i in range(1, n + 1):
			p2x, p2y = coordinates[i % n]
			if y > min(p1y, p2y):
				if y <= max(p1y, p2y):
					if x <= max(p1x, p2x):
						if p1y != p2y:
							xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
						if p1x == p2x or x <= xinters:
							inside = not inside
			p1x, p1y = p2x, p2y

		if not inside:
			args = [imei, latitude, longitude, alert_name, speed, zone, zone_alert, details]
			try:
				loop = asyncio.new_event_loop()
				loop.run_in_executor(None, device_not_keep_in_notification_sender, args)
			except(Exception)as e:
				pass
		elif inside:
			args = [imei, latitude, longitude, alert_name, speed, zone, zone_alert, details]
			try:
				loop = asyncio.new_event_loop()
				loop.run_in_executor(None, device_keep_in_notification_sender, args)
			except(Exception)as e:
				pass