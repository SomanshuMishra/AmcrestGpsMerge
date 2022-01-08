from django.conf import settings
from django.db import close_old_connections
import asyncio
import _thread

from app.models import Subscription, SettingsModel, Reports
from services.models import NotificationMessage

from .charging_notification_sender import *
from .charging_location_finder import *
from .sms_breakdown import *

from app.notification_saver.notification_saver import *


from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import time
import pytz


NOTE = '''<br>
<br>
<b>Note :</b><br>
1. If you are getting more number of emails and you don't want to get such  emails .Then update your settings as written below.<br>
&nbsp;&nbsp;Map ->Click on the device then go to settings->Then in All alerts section you can completely disable your email alerts or you can enable/disable individual section also.
<br>'''

# UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"

User = get_user_model()


def charging_on_notification_receiver(imei, details):
	# print(imei, details)
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	speed = details.get('speed')
	args = [imei, longitude, latitude, speed, details]
	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, charging_on_notification_maker, args)
	except(Exception)as e:
		close_old_connections()
		print(e)
		pass
	pass


def charging_off_notification_receiver(imei, details):
	# print(imei, details)
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	speed = details.get('speed')
	args = [imei, longitude, latitude, speed, details]
	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, charging_off_notification_maker, args)
	except(Exception)as e:
		close_old_connections()
		print(e)
		pass
	pass

def save_report(imei, details):
	serializers = ReportsSerializer(data=details)
	if serializers.is_valid():
		serializers.save()
	else:
		print(serializers.errors)
	close_old_connections()


def get_time_zone(imei):
	sub = Subscription.objects.filter(imei_no=imei).last()
	if sub:
		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
		close_old_connections()
		if user.time_zone:
			return user.time_zone
	return 'UTC'

def charging_on_notification_maker(args):
	imei = args[0]
	try:
		latitude = args[2]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[1]
	except(Exception)as e:
		longitude = None

	try:
		speed = args[3]
	except(Exception)as e:
		speed = 0

	try:
		details = args[4]
	except(Exception)as e:
		details = None

	setting_instance = SettingsModel.objects.filter(imei=imei).last()


	try:
		send_notification_flag = setting_instance.charging_notification
	except(Exception)as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.charging_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.charging_email
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
		battery_percentage = details.get('battery_percentage', None)
	except(Exception)as e:
		battery_percentage = None


	try:
		# address = get_location(longitude, latitude)
		address = 'Unknown'
	except(Exception)as e:
		address = 'Unknown'
		
	device_name = Subscription.objects.filter(imei_no=imei).last()

	if details:
		message_instance = NotificationMessage.objects.filter(protocol=details.get('report_name', None)).first()
		try:
			time_zone = get_time_zone(imei)
			time_timezone = datetime.now(pytz.timezone(time_zone))
			date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
		except(Exception)as e:
			print(e)
			time_timezone = datetime.now()
			date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass

		if message_instance:
			if device_name.device_name:
				message_title = message_instance.title.format(device_name.device_name, address, speed, date_to_be_send)
				message_body_email = str(device_name.device_name) +' : Charger Connected to the Device, on '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
			else:
				message_title = message_instance.title.format("Unknown Device", address, speed, date_to_be_send)
				message_body_email = 'Charger Connected to the Device, on '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)


			if device_name.device_name:
				message_body = message_instance.body.format(device_name.device_name, address, speed, date_to_be_send)
			else:
				message_body = message_instance.body.format("Unknown Device", address, speed, date_to_be_send)


			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = str(device_name.device_name)

		else:

			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Charger Connected'
			else:
				message_title = 'Charger Connected'

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Charger Connected to the Device, on '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = str(device_name.device_name) +' : Charger Connected to the Device, on '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
			else:
				message_body = 'Charger Connected to the Device, on '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = 'Charger Connected to the Device, on '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

			if device_name.device_name:
				message_body_to_save = str(device_name.device_name) +' : Charger Connected to the Device, on '+date_to_be_send
			else:
				message_body_to_save = 'Charger Connected to the Device, on '+ date_to_be_send


			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown Device'

	

	report_obj = {
		"imei":imei,
		"alert_name":'Charger Connected',
		"device_name":device_name_name,
		"event_type":'charging',
		"location":address,
		"longitude":longitude,
		"latitude":latitude,
		"type":"alert",
		"speed":speed,
		"notification_sent":True,
		"send_notification":send_notification_flag,
		"event": "connected",
		"battery_percentage" : battery_percentage
	}
	# _thread.start_new_thread(save_report, (imei, report_obj ))
	_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'charging', global_send_notification_flag))
	_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
	_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
	_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'charging', longitude, latitude))
	close_old_connections()




def charging_off_notification_maker(args):
	imei = args[0]
	try:
		latitude = args[2]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[1]
	except(Exception)as e:
		longitude = None

	try:
		speed = args[3]
	except(Exception)as e:
		speed = 0

	try:
		details = args[4]
	except(Exception)as e:
		details = None

	setting_instance = SettingsModel.objects.filter(imei=imei).last()


	try:
		send_notification_flag = setting_instance.charging_notification
	except(Exception)as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.charging_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.charging_email
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
		# address = get_location(longitude, latitude)
		address = 'Unknown'
	except(Exception)as e:
		print(e)
		address = 'Unknown'

	try:
		battery_percentage = details.get('battery_percentage', None)
	except(Exception)as e:
		battery_percentage = None
		
	device_name = Subscription.objects.filter(imei_no=imei).last()

	if details:

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass

		message_instance = NotificationMessage.objects.filter(protocol=details.get('report_name', None)).first()
		try:
			time_zone = get_time_zone(imei)
			time_timezone = datetime.now(pytz.timezone(time_zone))
			date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
		except(Exception)as e:
			print(e)
			time_timezone = datetime.now()
			date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

		if message_instance:
			if device_name.device_name:
				message_title = message_instance.title.format(device_name.device_name, address, speed, date_to_be_send)
			else:
				message_title = message_instance.title.format("Unknown Device", address, speed, date_to_be_send)


			if device_name.device_name:
				message_body = message_instance.body.format(device_name.device_name, address, speed, date_to_be_send)
				message_body_email = str(device_name.device_name) +' : Charger Disconnected, on '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
			else:
				message_body = message_instance.body.format("Unknown Device", address, speed, date_to_be_send)
				message_body_email = 'Charger Disconnected, on '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)


			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = str(device_name.device_name)
		else:

			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Charger Disconnected'
			else:
				message_title = 'Device Switched OFF'

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Charger Disconnected, on '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = str(device_name.device_name) +' : Charger Disconnected, on '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
			else:
				message_body = 'Charger Disconnected, on '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = 'Charger Disconnected, on '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

			if device_name.device_name:
				message_body_to_save = str(device_name.device_name) +' : Charger Disconnected, on '+date_to_be_send
			else:
				message_body_to_save = 'Charger Disconnected, on '+ date_to_be_send

			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown Device'

	

	report_obj = {
		"imei":imei,
		"alert_name":'Charger Disconnected',
		"device_name":device_name_name,
		"event_type":'charging',
		"location":address,
		"longitude":longitude,
		"latitude":latitude,
		"type":"alert",
		"speed":speed,
		"notification_sent":True,
		"send_notification":send_notification_flag,
		"event": "disconnected",
		"battery_percentage":battery_percentage
	}
	# _thread.start_new_thread(save_report, (imei, report_obj ))
	_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'charging', global_send_notification_flag ))
	_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
	_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
	_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'charging', longitude, latitude))
	close_old_connections()