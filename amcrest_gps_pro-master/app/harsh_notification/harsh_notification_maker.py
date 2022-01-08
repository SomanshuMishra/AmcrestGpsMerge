from django.conf import settings
from django.db import close_old_connections
import asyncio
import _thread

from app.models import Subscription, SettingsModel, Reports
from services.models import HarshNotificationMessage

from app.notification_saver.notification_saver import *


from .harsh_notification_sender import *
from .harsh_location_finder import *
from .harsh_types import *
from .sms_breakdown import *

from datetime import datetime, timedelta
import time
import pytz

from django.contrib.auth import get_user_model
User = get_user_model()



NOTE = '''<br>
<br>
<b>Note :</b><br>
1. If you are getting more number of emails and you don't want to get such  emails .Then update your settings as written below.<br>
&nbsp;&nbsp;Map ->Click on the device then go to settings->Then in All alerts section you can completely disable your email alerts or you can enable/disable individual section also.
<br>'''

# UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"


def harsh_notification_receiver(imei, details):
	# print(imei, details)
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	speed = details.get('speed')
	args = [imei, longitude, latitude, speed, details]
	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, harsh_notification_maker, args)
	except(Exception)as e:
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



# harsh_type = {
# 	"00":"unknow_speed_harsh_breaking_behaviour",
# 	"01": "unknow_speed_harsh_acceleration_behaviour",
# 	"02": "unknow_speed_harsh_turning_behaviour",
# 	"03": "unknow_speed_harsh_braking_and_turning_behaviour",
# 	"04": "unknow_speed_harsh_acceleration_and_turning_behaviour",
# 	"05": "unknow_speed_unknown_harsh_behaviour",

# 	"10": "low_speed_harsh_breaking_behaviour",
# 	"11": "low_speed_harsh_acceleration_behaviour",
# 	"12": "low_speed_harsh_turning_behaviour",
# 	"13": "low_speed_harsh_braking_and_turning_behaviour",
# 	"14": "low_speed_harsh_acceleration_and_turning_behaviour",
# 	"15": "low_speed_unknown_harsh_behaviour",

# 	"20": "medium_speed_harsh_breaking_behaviour",
# 	"21": "medium_speed_harsh_acceleration_behaviour",
# 	"22": "medium_speed_harsh_turning_behaviour",
# 	"23": "medium_speed_harsh_braking_and_turning_behaviour",
# 	"24": "medium_speed_harsh_acceleration_and_turning_behaviour",
# 	"25": "medium_speed_unknown_harsh_behaviour",

# 	"30": "high_speed_harsh_breaking_behaviour",
# 	"31": "high_speed_harsh_acceleration_behaviour",
# 	"32": "high_speed_harsh_turning_behaviour",
# 	"33": "high_speed_harsh_braking_and_turning_behaviour",
# 	"34": "high_speed_harsh_acceleration_and_turning_behaviour",
# 	"35": "high_speed_unknown_harsh_behaviour",
# }


# notification_harsh_type = {
# 	"0": "harsh_breaking",
# 	"1": "harsh_acceleration",
# 	"2": "harsh_turning",
# 	"3": "harsh_braking_and_turning",
# 	"4": "harsh_acceleration_and_turning",
# 	"5": "speed_unknown_harsh"
# }


def get_time_zone(imei):
	sub = Subscription.objects.filter(imei_no=imei).last()
	if sub:
		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
		if user.time_zone:
			return user.time_zone
	return 'UTC'


def get_mesurment_unit(imei):
	sub = Subscription.objects.filter(imei_no=imei).last()
	if sub:
		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).last()
		if user:
			return user.uom
		return 'kms'
	return 'kms'

def harsh_notification_maker(args):
	close_old_connections()
	imei = args[0]
	uom = get_mesurment_unit(imei)
	try:
		latitude = args[2]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[1]
	except(Exception)as e:
		longitude = None

	try:
		speed = float(args[3])
	except(Exception)as e:
		speed = 0

	try:
		details = args[4]
	except(Exception)as e:
		details = None


	try:
		if uom == 'miles':
			speed_message = str('%.2f'%(speed/1.60934))+' mph.'
		else:
			speed_message = str('%.2f'%speed)+' kmph.'
			
	except(Exception)as e:
		speed_message = str('%.2f'%speed)+' kmph.'

	setting_instance = SettingsModel.objects.filter(imei=imei).last()

	try:
		send_notification_flag = setting_instance.harshbraking_notification
	except(Exception)as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.harshbraking_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.harshbraking_email
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
		address = get_location(longitude, latitude)
	except(Exception)as e:
		print(e)
		address = 'Unknown'

	try:
		battery_percentage = details.get('battery_percentage', None)
	except(Exception)as e:
		battery_percentage = None
		
	device_name = Subscription.objects.filter(imei_no=imei).last()

	if details:
		message_instance = HarshNotificationMessage.objects.filter(report_type=details.get('report_type', None)).first()
		try:
			time_zone = get_time_zone(imei)
			time_timezone = datetime.now(pytz.timezone(time_zone))
			date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
		except(Exception)as e:
			time_timezone = datetime.now()
			date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass

		if message_instance:
			if device_name.device_name:
				message_title = message_instance.title.format(device_name.device_name, address, speed_message, date_to_be_send)
			else:
				message_title = message_instance.title.format("Unknown Device", address, speed_message, date_to_be_send)


			if device_name.device_name:
				message_body_to_save = message_instance.body.format(device_name.device_name, address, speed_message, date_to_be_send)
			else:
				message_body_to_save = message_instance.body.format("Unknown Device", address, speed_message, date_to_be_send)


			if device_name.device_name:
				message_body = message_body_to_save +' Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = message_body_to_save +' Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
			else:
				message_body = message_body_to_save +' Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = message_body_to_save +' Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)


			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = str(device_name.device_name)
		else:

			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Harsh Behaviour'
			else:
				message_title = 'Harsh Behaviour'

			if device_name.device_name:
				message_body_to_save = str(device_name.device_name) +' : Harsh Behaviour, at '+address+' location, and speed is '+ speed_message + ' On '+date_to_be_send
			else:
				message_body_to_save = 'Harsh Behaviour, at '+address+' location, and speed is '+ speed_message + ' On '+ date_to_be_send


			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Harsh Behaviour, at '+address+' location, and speed is '+ speed_message + ' On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = str(device_name.device_name) +' : Harsh Behaviour, at '+address+' location, and speed is '+ speed_message + ' On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
			else:
				message_body = 'Harsh Behaviour, at '+address+' location, and speed is '+ speed_message + ' On '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = 'Harsh Behaviour, at '+address+' location, and speed is '+ speed_message + ' On '+ date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown Device'

	try:
		event_type = harsh_type.get(details.get('report_type', None))
	except(Exception)as e:
		event_type = 'harsh_breaking_behaviour'

	try:
		notification_event_type = notification_harsh_type.get(details.get('report_type', None)[-1])
	except(Exception)as e:
		print(e)
		notification_event_type = 'harsh_breaking'

	report_obj = {
		"imei":imei,
		"alert_name":'Harsh Behaviour',
		"device_name":device_name_name,
		"event_type":event_type,
		"location":address,
		"longitude":longitude,
		"latitude":latitude,
		"type":"alert",
		"speed":speed,
		"notification_sent":True,
		"send_notification":send_notification_flag,
		"event": "harsh",
		"battery_percentage":battery_percentage
	}
	# _thread.start_new_thread(save_report, (imei, report_obj ))
	_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'harsh', global_send_notification_flag))
	_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
	_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
	_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'harsh', longitude, latitude))
	close_old_connections()