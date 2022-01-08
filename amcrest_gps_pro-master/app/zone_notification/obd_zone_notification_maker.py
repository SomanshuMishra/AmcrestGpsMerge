import asyncio
import datetime
import time
import pytz
import _thread

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import close_old_connections

from mongoengine.queryset.visitor import Q

from app.location_finder import *
from app.models import Subscription, SettingsModel, Reports, ZoneNotificationChecker, ZoneAlertObd
from app.serializers import ReportsSerializer, ZoneNotificationCheckerSerializer
from app.notification_saver.notification_saver import *

from .zone_notification_sender import send_notification
from .zone_location_finder import *
from .sms_breakdown import *

#================================Zone Notification============================
NOTE = '''<br>
<br>
<b>Note :</b><br>
1. If you are getting more number of emails and you don't want to get such  emails .Then update your settings as written below.<br>
&nbsp;&nbsp;Map ->Click on the device then go to settings->Then in All alerts section you can completely disable your email alerts or you can enable/disable individual section also.
<br>'''

# UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
def start_zone_notification(imei, details):
	if details.get('report_type'):
		if details.get('report_type')[1] == '1' or details.get('report_type')[1] == 1:
			alerts = ZoneAlertObd.objects.filter(imei=imei, zone_device_id=details.get('report_type')[0]).exclude(type='keep-in').last()
			if alerts:
				send_no_go_alert([imei, alerts, details])
		elif details.get('report_type')[1] == '0' or details.get('report_type')[1] == 0:
			alerts = ZoneAlertObd.objects.filter(imei=imei, zone_device_id=details.get('report_type')[0]).exclude(type='no-go').last()
			if alerts:
				send_keep_in_alert([imei, alerts, details])

def get_time_zone(imei):
	sub = Subscription.objects.filter(imei_no=imei).last()
	close_old_connections()
	if sub:
		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
		close_old_connections()
		if user.time_zone:
			return user.time_zone
	return 'UTC'


def send_no_go_alert(args):
	imei = args[0]
	details_dict = args[2]
	zone_alert_instance = args[1]

	try:
		latitude = details_dict.get('latitude')
	except(Exception)as e:
		latitude = None

	try:
		longitude = details_dict.get('longitude')
	except(Exception)as e:
		longitude = None

	try:
		zone_alert=zone_alert_instance.id
	except(Exception)as e:
		zone_alert = None

	try:
		if args[1]:
			alert_name = zone_alert_instance.name
		else:
			alert_name = "Unknown"
	except(Exception)as e:
		alert_name = "Unknown"


	try:
		speed = details_dict.get('speed')
	except(Exception)as e:
		speed = 0


	setting_instance = SettingsModel.objects.filter(imei=imei).last()

	try:
		send_notification_flag = setting_instance.zone_alert_notification
	except(Exception)as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.zone_alert_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.zone_alert_email
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
		time_zone = get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		time_timezone = datetime.datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

	address = get_location(longitude, latitude)
	device_name = Subscription.objects.filter(imei_no=imei).last()

	try:
		UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
		UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
	except(Exception)as e:
		pass

	if device_name.device_name:
		device_name_name = str(device_name.device_name)
	else:
		device_name_name = 'Unknown'

	if device_name.device_name:
		message_title = str(device_name.device_name) +' has entered zone '+alert_name+'.'
		# alert_name+' - '+str(device_name.device_name) +' : Vehicle enter into NO-GO zone. On '+date_to_be_send
		# str(device_name.device_name) +' device has left zone, at '+address+' location. On '+date_to_be_send
	else:
		message_title = str(imei) +' has entered zone '+alert_name+'.'

	if device_name.device_name:
		message_body = str(device_name.device_name) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
		message_body_email = str(device_name.device_name) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
	else:
		message_body = str(imei) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
		message_body_email = str(imei) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

	if device_name.device_name:
		message_body_to_save = str(device_name.device_name) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send
	else:
		message_body_to_save = str(imei) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send
	
	report_obj = {
		"imei":imei,
		"alert_name":alert_name,
		"device_name":device_name_name,
		"event_type":"no_go_zone",
		"battery_percentage":None,
		"location":address,
		"longitude":longitude,
		"latitude":latitude,
		"speed":speed,
		"type":"alert",
		"notification_sent":True,
		"zone":None,
		"zone_alert":None,
		"send_notification":send_notification_flag,
		"event": "entry"
	}
	_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'zone', global_send_notification_flag))
	_thread.start_new_thread(breakdown_obd_message, (imei, device_name.customer_id, message_title, message_body, zone_alert, global_send_sms_flag))
	_thread.start_new_thread(breakdown_obd_mail, (imei, device_name.customer_id, message_title, message_body_email, zone_alert, global_send_mail_flag))
	_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'zone', longitude, latitude))
	close_old_connections()



def send_keep_in_alert(args):
	imei = args[0]
	details_dict = args[2]
	zone_alert_instance = args[1]
	print(zone_alert_instance)
	try:
		latitude = details_dict.get('latitude')
	except(Exception)as e:
		latitude = None

	try:
		longitude = details_dict.get('longitude')
	except(Exception)as e:
		longitude = None

	try:
		zone_alert=zone_alert_instance.id
	except(Exception)as e:
		zone_alert = None

	try:
		if args[1]:
			alert_name = zone_alert_instance.name
		else:
			alert_name = "Unknown"
	except(Exception)as e:
		alert_name = "Unknown"


	try:
		speed = details_dict.get('speed')
	except(Exception)as e:
		speed = 0


	setting_instance = SettingsModel.objects.filter(imei=imei).last()

	try:
		send_notification_flag = setting_instance.zone_alert_notification
	except(Exception)as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.zone_alert_sms
	except(Exception)as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.zone_alert_email
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
		time_zone = get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		time_timezone = datetime.datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

	address = get_location(longitude, latitude)
	device_name = Subscription.objects.filter(imei_no=imei).last()

	try:
		UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
		UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
	except(Exception)as e:
		pass

	if device_name.device_name:
		device_name_name = str(device_name.device_name)
	else:
		device_name_name = 'Unknown'

	if device_name.device_name:
		message_title = str(device_name.device_name) +' has left zone '+alert_name+'.'
	else:
		message_title = str(imei)+' has left zone '+alert_name+'.'

	if device_name.device_name:
		message_body = str(device_name.device_name) +' has left zone, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
		message_body_email = str(device_name.device_name) +' has left zone, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
	else:
		message_body = str(imei)+' has left zone '+alert_name+', at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
		message_body_email = str(imei)+' has left zone '+alert_name+', at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

	if device_name.device_name:
		message_body_to_save = str(device_name.device_name) +' has left zone, at '+address+' location. On '+date_to_be_send
	else:
		message_body_to_save = str(imei)+' has left zone '+alert_name+', at '+address+' location. On '+date_to_be_send
	
	report_obj = {
		"imei":imei,
		"alert_name":alert_name,
		"device_name":device_name_name,
		"event_type":"out_of_zone",
		"battery_percentage":None,
		"location":address,
		"longitude":longitude,
		"latitude":latitude,
		"speed":speed,
		"type":"alert",
		"notification_sent":True,
		"zone":None,
		"zone_alert":zone_alert,
		"send_notification":send_notification_flag,
		"event": "exit"
	}
	_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'zone', global_send_notification_flag))
	_thread.start_new_thread(breakdown_obd_message, (imei, device_name.customer_id, message_title, message_body, zone_alert, global_send_sms_flag))
	_thread.start_new_thread(breakdown_obd_mail, (imei, device_name.customer_id, message_title, message_body_email, zone_alert, global_send_mail_flag))
	_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'zone', longitude, latitude))