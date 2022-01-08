from django.conf import settings
from django.db import close_old_connections
import asyncio
from .notification_sender import send_notification
from app.models import Subscription, SettingsModel
from app.serializers import ReportsSerializer
from .location_finder import *
from .sms_breakdown import *
import _thread

from app.notification_saver.notification_saver import *


import pytz
from datetime import datetime, timedelta
import time

# thread.start_new_thread( print_time, ("Thread-1", 2, ) )

# [{"lat":"20.354053","lng":"85.818847"},{"lat":"20.354113","lng":"85.820048"},{"lat":"20.353283","lng":"85.819769"},{"lat":"20.353338","lng":"85.819018"}]

NOTE = '''<br>
<br>
<b>Note :</b><br>
1. If you are getting more number of emails and you don't want to get such  emails .Then update your settings as written below.<br>
&nbsp;&nbsp;Map ->Click on the device then go to settings->Then in All alerts section you can completely disable your email alerts or you can enable/disable individual section also.
<br>'''

# UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"

#================================Engine Notification============================
def engine_started_notification_receiver(imei, details):
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	args = [imei, longitude, latitude]
	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, engine_started_notification_sender, args)
	except(Exception)as e:
		print(e)
		pass
	pass


def save_report(imei, details):
	serializer = ReportsSerializer(data=details)
	if serializer.is_valid():
		serializer.save()
	close_old_connections()



def get_time_zone(imei):
	sub = Subscription.objects.filter(imei_no=imei).last()
	close_old_connections()
	if sub:
		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
		close_old_connections()
		if user.time_zone:
			return user.time_zone
	return 'UTC'


def engine_started_notification_sender(args):
	close_old_connections()
	imei = args[0]
	try:
		latitude = args[2]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[1]
	except(Exception)as e:
		longitude = None

	setting_instance = SettingsModel.objects.filter(imei=imei).last()

	try:
		send_notification_flag = setting_instance.engine_notification
	except(Exception) as e:
		send_notification_flag = False


	try:
		send_sms_flag = setting_instance.engine_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.engine_email
	except(Exception)as e:
		send_mail_flag = False

	try:
		global_send_notification_flag = setting_instance.global_notification
	except(Exception) as e:
		global_send_notification_flag = False

	try:
		global_send_sms_flag = setting_instance.global_sms
	except(Exception) as e:
		global_send_sms_flag = False

	try:
		global_send_mail_flag = setting_instance.global_email
	except(Exception) as e:
		global_send_mail_flag = False

	# query = Q(event_type="trip_start") | Q(event_type="trip_end") | Q(event_type="engine_start") | Q(event_type="engine_stop")
	query = Q(event_type="engine_start") | Q(event_type="engine_stop")
	
	report_instance = Reports.objects.filter(query, imei=imei).order_by('-id').first()
	try:
		# check_trip = report_instance.event_type
		check_trip = "engine_stop"
	except(Exception)as e:
		check_trip = None


	try:
		time_zone = get_time_zone(imei)
		time_timezone = datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		time_timezone = datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

	if check_trip == None or check_trip == "engine_stop":

		try:
			address = get_location(longitude, latitude)
		except(Exception)as e:
			address = 'Unknown'

		device_name = Subscription.objects.filter(imei_no=imei).last()
		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Engine On'
		else:
			message_title = 'Engine On'

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Engine on, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = str(device_name.device_name) +' : Engine on, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
		else:
			message_body = 'Engine on, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = 'Engine on, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)


		if device_name.device_name:
			message_body_to_save = str(device_name.device_name) +' : Engine on, at '+address+' location. On '+date_to_be_send
		else:
			message_body_to_save = 'Engine on, at '+address+' location. On '+date_to_be_send

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		report_obj = {
			"imei":imei,
			"alert_name":'Engine on',
			"device_name":device_name_name,
			"event_type":"engine_start",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"type":"alert",
			"notification_sent":True,
			"send_notification":send_notification_flag,
			"event": "on"
		}
		report_instance_delete = Reports.objects.filter(query, imei=imei).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception)as e:
				pass
		
		_thread.start_new_thread(save_report, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'engine', global_send_notification_flag ))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'engine', longitude, latitude))
		close_old_connections()
	else:
		try:
			# address = get_location(longitude, latitude)
			address = 'Unknown'
		except(Exception)as e:
			address = 'Unknown'
		device_name = Subscription.objects.filter(imei_no=imei).last()
		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Engine on'
		else:
			message_title = 'Engine on'

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Engine on, at '+address+' location. On '+date_to_be_send
		else:
			message_body = 'Engine on, at '+address+' location. On '+date_to_be_send

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		report_obj = {
			"imei":imei,
			"alert_name":'Engine on',
			"device_name":device_name_name,
			"event_type":"engine_start",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"type":"alert",
			"notification_sent":False,
			"event": "on"
		}
		report_instance_delete = Reports.objects.filter(query, imei=imei).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception)as e:
				pass
		_thread.start_new_thread(save_report, (imei, report_obj ))
		close_old_connections()
	pass


			

def engine_turnoff_notification_receiver(imei, details):
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	args = [imei, longitude, latitude]
	
	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, engine_turnoff_notification_sender, args)
	except(Exception)as e:
		print(e)
		pass
	pass


def engine_turnoff_notification_sender(args):
	close_old_connections()
	imei = args[0]
	try:
		latitude = args[2]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[1]
	except(Exception)as e:
		longitude = None


	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	try:
		send_notification_flag = setting_instance.engine_notification
	except(Exception) as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.engine_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.engine_email
	except(Exception)as e:
		send_mail_flag = False

	try:
		global_send_notification_flag = setting_instance.global_notification
	except(Exception) as e:
		global_send_notification_flag = False

	try:
		global_send_sms_flag = setting_instance.global_sms
	except(Exception) as e:
		global_send_sms_flag = False

	try:
		global_send_mail_flag = setting_instance.global_email
	except(Exception) as e:
		global_send_mail_flag = False

	# query = Q(event_type="trip_start") | Q(event_type="trip_end") | Q(event_type="engine_start") | Q(event_type="engine_stop")
	query = Q(event_type="engine_start") | Q(event_type="engine_stop")
	report_instance = Reports.objects.filter(query, imei=imei).order_by('-id').first()
	
	try:
		check_trip = report_instance.event_type
		check_trip = "engine_start"
	except(Exception)as e:
		check_trip = None


	try:
		time_zone = get_time_zone(imei)
		time_timezone = datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		time_timezone = datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")


	if check_trip == "engine_start":

		try:
			address = get_location(longitude, latitude)
		except(Exception)as e:
			address = 'Unknown'
		device_name = Subscription.objects.filter(imei_no=imei).last()
		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Engine off'
		else:
			message_title = 'Engine off'

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Engine off, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = str(device_name.device_name) +' : Engine off, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
		else:
			message_body = 'Engine off, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = 'Engine off, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)


		if device_name.device_name:
			message_body_to_save = str(device_name.device_name) +' : Engine off, at '+address+' location. On '+date_to_be_send
		else:
			message_body_to_save = 'Engine off, at '+address+' location. On '+date_to_be_send

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'
		
		report_obj = {
			"imei":imei,
			"alert_name":'Engine Off',
			"device_name":device_name_name,
			"event_type":"engine_stop",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"type":"alert",
			"notification_sent":True,
			"send_notification":send_notification_flag,
			"event": "off"
		}

		report_instance_delete = Reports.objects.filter(query, imei=imei).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception)as e:
				pass

		_thread.start_new_thread(save_report, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'engine', global_send_notification_flag ) )
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'engine', longitude, latitude))
		close_old_connections()

	else:
		try:
			# address = get_location(longitude, latitude)
			address = 'Unknown'
		except(Exception)as e:
			address = 'Unknown'
		device_name = Subscription.objects.filter(imei_no=imei).last()
		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Engine off'
		else:
			message_title = 'Engine off'

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Engine off, at '+address+' location. On '+date_to_be_send
		else:
			message_body = 'Engine off, at '+address+' location. On '+date_to_be_send

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'
		
		report_obj = {
			"imei":imei,
			"alert_name":'Engine off',
			"device_name":device_name_name,
			"event_type":"engine_stop",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"type":"alert",
			"notification_sent":False,
			"event": "off"
		}

		report_instance_delete = Reports.objects.filter(query, imei=imei).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception)as e:
				pass
				
		_thread.start_new_thread(save_report, (imei, report_obj ))
		close_old_connections()
	pass