from django.conf import settings
from django.db import close_old_connections
import asyncio
import _thread
import time
import datetime

from app.models import Subscription, SettingsModel, Reports
from app.serializers import ReportsSerializer

from app.notification_saver.notification_saver import *


from .trip_notification_sender import *
from .trip_location_finder import *
from .sms_breakdown import *

NOTE = '''<br>
<br>
<b>Note :</b><br>
1. If you are getting more number of emails and you don't want to get such  emails .Then update your settings as written below.<br>
&nbsp;&nbsp;Map ->Click on the device then go to settings->Then in All alerts section you can completely disable your email alerts or you can enable/disable individual section also.
<br>'''

UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"

def save_report(imei, details):
	serializers = ReportsSerializer(data=details)
	if serializers.is_valid():
		serializers.save()
	close_old_connections()


def get_time_zone(imei):
	sub = Subscription.objects.filter(imei_no=imei).last()
	close_old_connections()
	if sub:
		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
		if user:
			close_old_connections()
			return user.time_zone
	return 'UTC'

def trip_end_notification_receiver(imei, details):
	_thread.start_new_thread(trip_end_notification_checker, (imei, details))


def trip_end_immidiate_notification_receiver(imei, details):
	_thread.start_new_thread(trip_end_immidiate_notification_checker, (imei, details))


def trip_end_notification_checker(imei, details):
	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	try:
		send_notification_flag = setting_instance.trip_notification
	except(Exception)as e:
		send_notification_flag = False


	try:
		send_sms_flag = setting_instance.trip_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.trip_email
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

	query = Q(event_type="trip_start") | Q(event_type="trip_end")
	report_instance1 = Reports.objects.filter(query, imei=imei).all()


	try:
		speed = details.get('speed', None)
	except(Exception)as e:
		speed = None
	
	report_instance = Reports.objects.filter(query, imei=imei).order_by('-id').first()
	close_old_connections()

	try:
		check_trip = report_instance.event_type
	except(Exception)as e:
		check_trip = None

	check_trip_running = None
	if not check_trip_running:
		if check_trip == 'trip_start' or check_trip == "trip_end":
			try:
				time_zone = get_time_zone(imei)
				time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
				date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
			except(Exception)as e:
				time_timezone = datetime.datetime.now()
				date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

			try:
				longitude = details.get('longitude', None)
				latitude = details.get('latitude', None)
			except(Exception)as e:
				longitude = None
				latitude = None

			address = get_location(longitude, latitude)
			device_name = Subscription.objects.filter(imei_no=imei).last()

			try:
				UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
			except(Exception)as e:
				pass

			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Motion Stopped. On '+date_to_be_send
			else:
				message_title = 'Motion Stopped. On '+date_to_be_send

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}'.format(latitude, longitude, NOTE)
			else:
				message_body = 'Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = 'Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}'.format(latitude, longitude, NOTE)


			if device_name.device_name:
				message_body_to_save = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send
			else:
				message_body_to_save = 'Motion Stopped, at '+address+' location. On '+date_to_be_send

			report_obj = {
					"imei":imei,
					"alert_name":'Motion Stopped',
					"device_name":device_name_name,
					"event_type":"trip_end",
					"location":address,
					"longitude":longitude,
					"latitude":latitude,
					"type":"alert",
					"notification_sent":True,
					"send_notification":send_notification_flag,
					"event":"ended",
					"speed":speed
				}

			report_instance_delete = Reports.objects.filter(query, imei=imei).all()
			if report_instance_delete:
				try:
					report_instance_delete.delete()
				except(Exception)as e:
					pass

			_thread.start_new_thread(save_report, (imei, report_obj ))
			_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'trip', global_send_notification_flag))
			_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
			_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
			_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'trip', longitude, latitude))
			close_old_connections()

		else:
			try:
				time_zone = get_time_zone(imei)
				time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
				date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
			except(Exception)as e:
				time_timezone = datetime.datetime.now()
				date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

			try:
				longitude = details.get('longitude', None)
				latitude = details.get('latitude', None)
			except(Exception)as e:
				longitude = None
				latitude = None

			# address = get_location(longitude, latitude)
			address = "Unknown"
			device_name = Subscription.objects.filter(imei_no=imei).last()

			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Motion Stopped. On '+date_to_be_send
			else:
				message_title = 'Motion Stopped.'

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send
			else:
				message_body = 'Motion Stopped, at '+address+' location. On '+date_to_be_send

			report_obj = {
					"imei":imei,
					"alert_name":'Motion Stopped',
					"device_name":device_name_name,
					"event_type":"trip_end",
					"location":address,
					"longitude":longitude,
					"latitude":latitude,
					"type":"alert",
					"notification_sent":False
				}

			report_instance_delete = Reports.objects.filter(query, imei=imei).all()
			if report_instance_delete:
				try:
					report_instance_delete.delete()
				except(Exception)as e:
					pass

			_thread.start_new_thread(save_report, (imei, report_obj ))
			close_old_connections()


def trip_start_notification_receiver(imei, details):
	print(details)
	close_old_connections()
	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	try:
		send_notification_flag = setting_instance.trip_notification
	except(Exception)as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.trip_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.trip_email
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

	try:
		speed = details.get('speed', None)
	except(Exception)as e:
		speed = None

	close_old_connections()
	# time.sleep(2)
	# query = Q(event_type="trip_start") | Q(event_type="trip_end") | Q(event_type="engine_start") | Q(event_type="engine_stop")
	query = Q(event_type="trip_start") | Q(event_type="trip_end")

	report_instance = Reports.objects.filter(query, imei=imei).order_by('-id').first()

	
	try:
		check_trip = report_instance.event_type
	except(Exception)as e:
		check_trip = None

	try:
		time_zone = get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		print(e)
		time_timezone = datetime.datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

	print(details)
	if check_trip == 'trip_end' or check_trip == None or check_trip == "engine_stop" or check_trip == "trip_start":
		try:
			longitude = details.get('longitude', None)
			latitude = details.get('latitude', None)
		except(Exception)as e:
			longitude = None
			latitude = None

		address = get_location(longitude, latitude)
		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		try:
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass

		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Motion Started. On '+date_to_be_send
		else:
			message_title = 'Motion Started. On '+date_to_be_send

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Motion Started, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = str(device_name.device_name) +' : Motion Started, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
		else:
			message_body = 'Motion Started, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = 'Motion Started, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

		if device_name.device_name:
			message_body_to_save = str(device_name.device_name) +' : Motion Started, at '+address+' location. On '+date_to_be_send
		else:
			message_body_to_save = 'Motion Started, at '+address+' location. On '+date_to_be_send

		report_obj = {
				"imei":imei,
				"alert_name":'Motion Started',
				"device_name":device_name_name,
				"event_type":"trip_start",
				"location":address,
				"longitude":longitude,
				"latitude":latitude,
				"type":"alert",
				"notification_sent":True,
				"send_notification":send_notification_flag,
				"event":"started",
				"speed":speed
			}

		report_instance_delete = Reports.objects.filter(query, imei=imei).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception)as e:
				pass

		_thread.start_new_thread(save_report, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'trip', global_send_notification_flag))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'trip', longitude, latitude))
		close_old_connections()

	else:
		try:
			longitude = details.get('longitude', None)
			latitude = details.get('latitude', None)
		except(Exception)as e:
			longitude = None
			latitude = None

		# address = get_location(longitude, latitude)
		address = "Unknown"
		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Motion Started. On '+date_to_be_send
		else:
			message_title = 'Motion Started. On '+date_to_be_send

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Motion Started, at '+address+' location. On '+date_to_be_send
		else:
			message_body = 'Motion Started, at '+address+' location. On '+date_to_be_send

		report_obj = {
				"imei":imei,
				"alert_name":'Motion Started',
				"device_name":device_name_name,
				"event_type":"trip_start",
				"location":address,
				"longitude":longitude,
				"latitude":latitude,
				"type":"alert",
				"notification_sent":False,
				"speed":speed
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




def trip_end_immidiate_notification_checker(imei, details):
	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	close_old_connections()
	try:
		send_notification_flag = setting_instance.trip_notification
	except(Exception)as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.trip_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.trip_email
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

	try:
		speed = details.get('speed', None)
	except(Exception)as e:
		speed = None


	# query = Q(event_type="trip_start") | Q(event_type="trip_end") | Q(event_type="engine_start") | Q(event_type="engine_stop")
	query = Q(event_type="trip_start") | Q(event_type="trip_end")
	report_instance = Reports.objects.filter(query, imei=imei).order_by('-id').first()


	try:
		check_trip = report_instance.event_type
	except(Exception)as e:
		check_trip = None


	check_trip_running = None
	if not check_trip_running:
		if check_trip == 'trip_start' or check_trip == "engine_start" or check_trip == "trip_end":
			try:
				time_zone = get_time_zone(imei)
				time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
				date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
			except(Exception)as e:
				print(e)
				time_timezone = datetime.datetime.now()
				date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

			try:
				longitude = details.get('longitude', None)
				latitude = details.get('latitude', None)
			except(Exception)as e:
				longitude = None
				latitude = None

			address = get_location(longitude, latitude)
			device_name = Subscription.objects.filter(imei_no=imei).last()

			try:
				UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
			except(Exception)as e:
				pass

			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Motion Stopped. On '+date_to_be_send
			else:
				message_title = 'Motion Stopped. On '+date_to_be_send

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}'.format(latitude, longitude, NOTE)
			else:
				message_body = 'Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = 'Motion Stopped, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}'.format(latitude, longitude, NOTE)


			if device_name.device_name:
				message_body_to_save = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send
			else:
				message_body_to_save = 'Motion Stopped, at '+address+' location. On '+date_to_be_send

			report_obj = {
					"imei":imei,
					"alert_name":'Motion Stopped',
					"device_name":device_name_name,
					"event_type":"trip_end",
					"location":address,
					"longitude":longitude,
					"latitude":latitude,
					"type":"alert",
					"notification_sent":True,
					"send_notification":send_notification_flag,
					"event":"ended",
					"speed":speed
				}
			report_instance_delete = Reports.objects.filter(query, imei=imei).all()
			if report_instance_delete:
				try:
					report_instance_delete.delete()
				except(Exception)as e:
					pass

			_thread.start_new_thread(save_report, (imei, report_obj ))
			_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'trip', global_send_notification_flag))
			_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
			_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
			_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'trip', longitude, latitude))
			close_old_connections()

		else:
			try:
				time_zone = get_time_zone(imei)
				time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
				date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
			except(Exception)as e:
				time_timezone = datetime.datetime.now()
				date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

			try:
				longitude = details.get('longitude', None)
				latitude = details.get('latitude', None)
			except(Exception)as e:
				longitude = None
				latitude = None

			# address = get_location(longitude, latitude)
			address = "Unknown"
			
			device_name = Subscription.objects.filter(imei_no=imei).last()

			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Motion Stopped. On '+date_to_be_send
			else:
				message_title = 'Motion Stopped. On '+date_to_be_send

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Motion Stopped, at '+address+' location. On '+date_to_be_send
			else:
				message_body = 'Motion Stopped, at '+address+' location. On '+date_to_be_send

			report_obj = {
					"imei":imei,
					"alert_name":'Motion Stopped',
					"device_name":device_name_name,
					"event_type":"trip_end",
					"location":address,
					"longitude":longitude,
					"latitude":latitude,
					"type":"alert",
					"notification_sent":False,
					"speed":speed
				}
				
			report_instance_delete = Reports.objects.filter(query, imei=imei).all()
			if report_instance_delete:
				try:
					report_instance_delete.delete()
				except(Exception)as e:
					pass

			_thread.start_new_thread(save_report, (imei, report_obj ))
			close_old_connections()