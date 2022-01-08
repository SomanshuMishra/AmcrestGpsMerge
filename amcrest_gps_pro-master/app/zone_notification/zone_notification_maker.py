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
from app.models import Subscription, SettingsModel, Reports, ZoneNotificationChecker
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

def save_report(imei, details):
	serializers = ReportsSerializer(data=details)
	if serializers.is_valid():
		serializers.save()
	close_old_connections()


def save_notification_checker(imei, details):
	serializer = ZoneNotificationCheckerSerializer(data=details)
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


def device_not_keep_in_notification_sender(args):
	imei = args[0]
	try:
		latitude = args[1]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[2]
	except(Exception)as e:
		longitude = None

	try:
		if args[3]:
			alert_name = args[3]
		else:
			alert_name = "Unknown"
	except(Exception)as e:
		alert_name = "Unknown"

	try:
		speed = args[4]
	except(Exception)as e:
		speed = 0

	try:
		zone_id = args[5]
	except(Exception)as e:
		zone_id = None


	try:
		zone_alert = args[6]
	except(Exception)as e:
		zone_alert = None

	try:
		details = args[7]
	except(Exception)as e:
		details = {}

	try:
		battery_percentage = details.get('battery_percentage')
	except(Exception)as e:
		battery_percentage = None

	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	close_old_connections()

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

	query = Q(event_type="out_of_zone") | Q(event_type="keep_in")
	report_instance = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).order_by('-id').first()
	close_old_connections()

	try:
		check_notification = report_instance.event_type
	except(Exception)as e:
		check_notification = None

	try:
		time_zone = get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		time_timezone = datetime.datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")
		pass

	if check_notification == 'keep_in':
		try:
			address = get_location(longitude, latitude)
		except(Exception)as e:
			print(e)
			address = 'Unknown'
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
			"battery_percentage":battery_percentage,
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"speed":speed,
			"type":"alert",
			"notification_sent":True,
			"zone":zone_id,
			"zone_alert":zone_alert,
			"send_notification":send_notification_flag,
			"event": "exit"
		}
		# _thread.start_new_thread(save_report, (imei, report_obj ))

		report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception) as e:
				pass

		_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'zone', global_send_notification_flag))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, zone_alert, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, zone_alert, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'zone', longitude, latitude))
		close_old_connections()
	else:
		address = 'Unknown'
		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = str(device_name.device_name) +' has left zone '+alert_name+'.'
		else:
			message_title = 'Device out of the zone'

		if device_name.device_name:
			message_body = str(device_name.device_name) +' has left zone, at '+address+' location.'
		else:
			message_body = 'Vehicle out from keep in zone, at '+address+' location.'
		
		report_obj = {
			"imei":imei,
			"alert_name":alert_name,
			"device_name":device_name_name,
			"event_type":"out_of_zone",
			"battery_percentage":battery_percentage,
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"speed":speed,
			"type":"alert",
			"notification_sent":False,
			"zone":zone_id,
			"zone_alert":zone_alert
		}

		# _thread.start_new_thread(save_report, (imei, report_obj ))
		report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception) as e:
				pass
		_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
		close_old_connections()
	pass


def device_keep_in_notification_sender(args):
	imei = args[0]
	try:
		latitude = args[1]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[2]
	except(Exception)as e:
		longitude = None

	try:
		if args[3]:
			alert_name = args[3]
		else:
			alert_name = "Unknown"
	except(Exception)as e:
		alert_name = "Unknown"

	try:
		speed = args[4]
	except(Exception)as e:
		speed = 0

	try:
		zone_id = args[5]
	except(Exception)as e:
		zone_id = None


	try:
		zone_alert = args[6]
	except(Exception)as e:
		zone_alert = None 

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



	query = Q(event_type="out_of_zone") | Q(event_type="keep_in")
	report_instance = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).order_by('-id').first()

	try:
		check_notification = report_instance.event_type
	except(Exception)as e:
		check_notification = None

	try:
		time_zone = get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		print(e)
		time_timezone = datetime.datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

	if check_notification == 'out_of_zone' or check_notification is None:
		# address = get_location(longitude, latitude)
		address = 'Unknown'
		device_name = Subscription.objects.filter(imei_no=imei).last()



		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = alert_name+' - '+str(device_name.device_name) +' : Vehicle in KEEP-IN zone. On '+date_to_be_send
		else:
			message_title = 'Vehicle out of the zone. On '+date_to_be_send

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Vehicle in KEEP-IN zone, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = str(device_name.device_name) +' : Vehicle in KEEP-IN zone, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}'.format(latitude, longitude, NOTE)
		else:
			message_body = 'Vehicle in KEEP-IN zone, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = 'Vehicle in KEEP-IN zone, at '+address+' location. On '+date_to_be_send+'. Google Map - https://maps.google.com/?q={},{}. {}'.format(latitude, longitude, NOTE)

		if device_name.device_name:
			message_body_to_save = str(device_name.device_name) +' : Vehicle in KEEP-IN zone, at '+address
		else:
			message_body_to_save = 'Vehicle in KEEP-IN zone, at '+address+' location. On '+date_to_be_send
		
		report_obj = {
			"imei":imei,
			"alert_name":alert_name,
			"device_name":device_name_name,
			"event_type":"keep_in",
			"battery_percentage":"2",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"speed":speed,
			"type":"alert",
			"notification_sent":True,
			"zone":zone_id,
			"zone_alert":zone_alert,
			"send_notification":send_notification_flag,
			"event": "entry"
		}

		# _thread.start_new_thread(save_report, (imei, report_obj ))

		report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception) as e:
				pass

		_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
		close_old_connections()
		# _thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'zone' ))
	else:
		# address = get_location(longitude, latitude)
		address = 'Unknown'
		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = alert_name+' - '+str(device_name.device_name) +' : Vehicle in KEEP-IN zone. On '+date_to_be_send
		else:
			message_title = 'Vehicle out of the zone. On '+date_to_be_send

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Vehicle in KEEP-IN zone, at '+address+' location. On '+date_to_be_send
		else:
			message_body = 'Vehicle in KEEP-IN zone, at '+address+' location. On '+date_to_be_send
		
		report_obj = {
			"imei":imei,
			"alert_name":alert_name,
			"device_name":device_name_name,
			"event_type":"keep_in",
			"battery_percentage":"2",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"speed":speed,
			"type":"alert",
			"notification_sent":False,
			"zone":zone_id,
			"zone_alert":zone_alert,
			"send_notification":send_notification_flag
		}

		# _thread.start_new_thread(save_report, (imei, report_obj ))

		report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception) as e:
				pass

		_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
		close_old_connections()
	pass




def device_no_go_notification_sender(args):
	imei = args[0]
	try:
		latitude = args[1]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[2]
	except(Exception)as e:
		longitude = None


	try:
		if args[3]:
			alert_name = args[3]
		else:
			alert_name = "Unknown"
	except(Exception)as e:
		alert_name = "Unknown"

	try:
		speed = args[4]
	except(Exception)as e:
		speed = 0

	try:
		zone_id = args[5]
	except(Exception)as e:
		zone_id = None

	try:
		details = args[7]
	except(Exception)as e:
		details = {}

	try:
		battery_percentage = details.get('battery_percentage', None)
	except(Exception)as e:
		battery_percentage = None


	try:
		zone_alert = args[6]
	except(Exception)as e:
		zone_alert = None 

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

	query = Q(event_type="no_go_zone") | Q(event_type="out_no_go_zone")
	report_instance = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).order_by('-id').first()
	close_old_connections()
	
	try:
		check_notification = report_instance.event_type
	except(Exception)as e:
		check_notification = None

	try:
		time_zone = get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		time_timezone = datetime.datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

	if check_notification == 'out_no_go_zone' or check_notification is None:
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
			"battery_percentage":battery_percentage,
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"speed":speed,
			"type":"alert",
			"notification_sent":True,
			"zone":zone_id,
			"zone_alert":zone_alert,
			"send_notification":send_notification_flag,
			"event": "entry"
		}

		# _thread.start_new_thread(save_report, (imei, report_obj ))

		report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception) as e:
				pass

		_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'zone', global_send_notification_flag))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, zone_alert, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, zone_alert, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'zone', longitude, latitude))
		close_old_connections()
	else:
		if send_notification_flag:
			# address = get_location(longitude, latitude)
			address = 'Unknown'
			device_name = Subscription.objects.filter(imei_no=imei).last()
			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			if device_name.device_name:
				message_title = str(device_name.device_name) +' has entered zone '+alert_name+'.'
			else:
				message_title = str(imei) +' has entered zone '+alert_name+'.'

			if device_name.device_name:
				message_body = str(device_name.device_name) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send
			else:
				message_body = str(imei) +' has entered zone '+alert_name+', at '+address+' location. On '+date_to_be_send
			
			report_obj = {
				"imei":imei,
				"alert_name":alert_name,
				"device_name":device_name_name,
				"event_type":"no_go_zone",
				"battery_percentage":battery_percentage,
				"location":address,
				"longitude":longitude,
				"latitude":latitude,
				"speed":speed,
				"type":"alert",
				"notification_sent":False,
				"zone":zone_id,
				"zone_alert":zone_alert
			}

			report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
			if report_instance_delete:
				try:
					report_instance_delete.delete()
				except(Exception) as e:
					pass

			_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
			# _thread.start_new_thread(save_report, (imei, report_obj ))


			close_old_connections()
	pass


def device_out_no_go_notification_sender(args):
	imei = args[0]
	try:
		latitude = args[1]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[2]
	except(Exception)as e:
		longitude = None


	try:
		if args[3]:
			alert_name = args[3]
		else:
			alert_name = "Unknown"
	except(Exception)as e:
		alert_name = "Unknown"

	try:
		speed = args[4]
	except(Exception)as e:
		speed = 0

	try:
		zone_id = args[5]
	except(Exception)as e:
		zone_id = None


	try:
		zone_alert = args[6]
	except(Exception)as e:
		zone_alert = None 

	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	close_old_connections()
	
	try:
		send_notification_flag = setting_instance.zone_alert_notification
	except(Exception)as e:
		send_notification_flag = False




	query = Q(event_type="no_go_zone") | Q(event_type="out_no_go_zone")
	report_instance = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).order_by('-id').first()
	close_old_connections()

	try:
		time_zone = get_time_zone(imei)
		time_timezone = datetime.datetime.now(pytz.timezone(time_zone))
		date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
	except(Exception)as e:
		time_timezone = datetime.datetime.now()
		date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")
	
	try:
		check_notification = report_instance.event_type
	except(Exception)as e:
		check_notification = None


	if check_notification == 'no_go_zone' or check_notification is None:
		if setting_instance:
			# address = get_location(longitude, latitude)
			address = 'Unknown'
			device_name = Subscription.objects.filter(imei_no=imei).last()
			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			if device_name.device_name:
				message_title = alert_name+' - '+str(device_name.device_name) +' : out from NO-GO zone.'
			else:
				message_title = 'Vehicle out from NO-GO zone. On '+date_to_be_send

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Vehicle out from NO-GO zone, at '+address+' location. On '+date_to_be_send
			else:
				message_body = 'Vehicle out from NO-GO zone, at '+address+' location. On '+date_to_be_send

			if device_name.device_name:
				message_body_to_save = str(device_name.device_name) +' : Vehicle out from NO-GO zone, at '+address+' location. On '+date_to_be_send
			else:
				message_body_to_save = 'Vehicle out from NO-GO zone, at '+address+' location. On '+date_to_be_send
			
			report_obj = {
				"imei":imei,
				"alert_name":alert_name,
				"device_name":device_name_name,
				"event_type":"out_no_go_zone",
				"battery_percentage":"2",
				"location":address,
				"longitude":longitude,
				"latitude":latitude,
				"speed":speed,
				"type":"alert",
				"notification_sent":True,
				"zone":zone_id,
				"zone_alert":zone_alert,
				"send_notification":send_notification_flag
			}
			# _thread.start_new_thread(save_report, (imei, report_obj ))

			report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
			if report_instance_delete:
				try:
					report_instance_delete.delete()
				except(Exception) as e:
					pass

			_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
			close_old_connections()
			# _thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'zone_no_go' ))
	else:
		if send_notification_flag:
			# address = get_location(longitude, latitude)
			address = 'Unknown'
			device_name = Subscription.objects.filter(imei_no=imei).last()
			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			if device_name.device_name:
				message_title = alert_name+' - '+str(device_name.device_name) +' : Vehicle out from NO-GO zone. On '+date_to_be_send
			else:
				message_title = 'Vehicle out from NO-GO zone. On '+date_to_be_send

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Vehicle out from NO-GO zone, at '+address+' location. On '+date_to_be_send
			else:
				message_body = 'Vehicle out from NO-GO zone, at '+address+' location. On '+date_to_be_send
			
			report_obj = {
				"imei":imei,
				"alert_name":alert_name,
				"device_name":device_name_name,
				"event_type":"out_no_go_zone",
				"battery_percentage":"2",
				"location":address,
				"longitude":longitude,
				"latitude":latitude,
				"speed":speed,
				"type":"alert",
				"notification_sent":False,
				"zone":zone_id,
				"zone_alert":zone_alert
			}

			# _thread.start_new_thread(save_report, (imei, report_obj ))

			report_instance_delete = ZoneNotificationChecker.objects.filter(query, imei=imei, zone=zone_id, zone_alert=zone_alert).all()
			if report_instance_delete:
				try:
					report_instance_delete.delete()
				except(Exception) as e:
					pass
				
			_thread.start_new_thread(save_notification_checker, (imei, report_obj ))
			close_old_connections()
	pass