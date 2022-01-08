import asyncio
import _thread

from datetime import datetime

from django.conf import settings
from django.db import close_old_connections

from app.models import Subscription, SettingsModel
from app.serializers import ReportsSerializer
from app.notification_saver.notification_saver import *

from .alert_notification_sender import send_notification
from .location_finder import *
from .sms_breakdown import *


#================================Engine Notification============================
NOTE = '''<br>
<br>
<b>Note :</b><br>
1. If you are getting more number of emails and you don't want to get such  emails .Then update your settings as written below.<br>
&nbsp;&nbsp;Map ->Click on the device then go to settings->Then in All alerts section you can completely disable your email alerts or you can enable/disable individual section also.
<br>'''

# UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"

def alert_notification_receiver(imei, details):
	args = [imei, details]
	try:
		# alert_notification_sender_function(args)
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, alert_notification_sender_function, args)
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

def alert_notification_sender_function(args):
	imei = args[0]
	details = args[1]

	
	try:
		setting_instance = SettingsModel.objects.filter(imei=imei).last()
	except(Exception)as e:
		print(e)
		setting_instance= None


	if setting_instance:

		try:
			latitude = details.get('latitude', None)
		except(Exception)as e:
			latitude = None

		try:
			speed = details.get('speed', None)
		except(Exception)as e:
			speed = 0

		try:
			battery_percentage = details.get('battery_percentage', None)
		except(Exception)as e:
			battery_percentage = None

		try:
			longitude = details.get('longitude', None)
		except(Exception)as e:
			longitude = None

		try:
			send_notification_flag = setting_instance.tow_notification
		except(Exception) as e:
			send_notification_flag = False


		try:
			send_sms_flag = setting_instance.tow_sms
		except(Exception)as e:
			send_sms_flag = False

		try:
			send_mail_flag = setting_instance.tow_email
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
			from datetime import datetime
			time_zone = get_time_zone(imei)
			time_timezone = datetime.now(pytz.timezone(time_zone))
			date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
		except(Exception)as e:
			time_timezone = datetime.now()
			date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")


		try:
			address = get_location(longitude, latitude)
		except(Exception)as e:
			address = 'Unknown'

		device_name = Subscription.objects.filter(imei_no=imei).last()
		
		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Vehicle Towing'
		else:
			message_title = 'Vehicle Towing'

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Vehicle Towing, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = str(device_name.device_name) +' : Vehicle Towing, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
		else:
			message_body = 'Vehicle Towing, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = 'Vehicle Towing, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

		if device_name.device_name:
			message_body_to_save = str(device_name.device_name) +' : Vehicle Towing, at '+address+' location. On '+date_to_be_send
		else:
			message_body_to_save = 'Vehicle Towing, at '+address+' location. On '+date_to_be_send

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		report_obj = {
			"imei":imei,
			"alert_name":'Vehicle Towing',
			"device_name":device_name_name,
			"event_type":"towing",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"type":"alert",
			"notification_sent":True,
			"send_notification":send_notification_flag,
			"event": None,
			"speed" : speed,
			"battery_percentage":battery_percentage
		}
		# _thread.start_new_thread(save_report, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'towing', global_send_notification_flag))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body,  send_sms_flag, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'towing', longitude, latitude))
		# _thread.start_new_thread(save_notifications, (imei, message_title, message_body, device_name.customer_id, 'trip'))