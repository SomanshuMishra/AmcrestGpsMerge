from django.conf import settings
from django.db import close_old_connections
import asyncio
import _thread

from .battery_notification_sender import *
from .battery_location_finder import *
from .sms_breakdown import *

from app.models import Subscription, SettingsModel, Reports
from app.serializers import ReportsSerializer
from app.notification_saver.notification_saver import *

from services.models import *


# thread.start_new_thread( print_time, ("Thread-1", 2, ) )

# [{"lat":"20.354053","lng":"85.818847"},{"lat":"20.354113","lng":"85.820048"},{"lat":"20.353283","lng":"85.819769"},{"lat":"20.353338","lng":"85.819018"}]


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
	

def battery_notification_receiver(imei, details):
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	battery_percentage = details.get('battery_percentage')
	speed = details.get('speed', None)
	args = [imei, longitude, latitude, battery_percentage, speed]

	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, battery_notification_maker, args)
	except(Exception)as e:
		close_old_connections()
		pass
	pass



def battery_notification_maker(args):
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
		battery_percentage = float(args[3])
	except(Exception)as e:
		battery_percentage = 0

	try:
		speed = float(args[4])
	except(Exception)as e:
		speed = 0

	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	
	try:
		send_notification_flag = setting_instance.battery_notification
	except(Exception) as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.battery_sms
	except(Exception) as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.battery_email
	except(Exception) as e:
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

	report_instance = Reports.objects.filter(event_type='battery', imei=imei).order_by('-id').first()

	try:
		battery_low_limit = float(setting_instance.battery_low_limit)
	except(Exception)as e:
		battery_low_limit = 0

	try:
		battery_lowest = AppConfiguration.objects.filter(key_name='lowest_battery_point').last()
		if battery_lowest:
			battery_lowest_point =  int(battery_lowest.key_value)
		else:
			battery_lowest_point =  5
	except(Exception)as e:
		battery_lowest_point = 5

	if battery_percentage != 0 and battery_percentage != None:
		if battery_low_limit > battery_percentage:
			try:
				# address = get_location(longitude, latitude)
				address = "Unknown"
			except(Exception)as e:
				address = "Unknown"

			device_name = Subscription.objects.filter(imei_no=imei).last()
			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Battery Low'
			else:
				message_title = 'Battery Low'

			try:
				UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
				UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
			except(Exception)as e:
				pass

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Battery Low - '+str(battery_percentage)+'%. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = str(device_name.device_name) +' : Battery Low - '+str(battery_percentage)+'%. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
			else:
				message_body = 'Battery Low - '+str(battery_percentage)+'%. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
				message_body_email = 'Battery Low - '+str(battery_percentage)+'%. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
				

			if device_name.device_name:
				message_body_to_save = str(device_name.device_name) +' : Battery Low - '+str(battery_percentage)+'%.'
			else:
				message_body_to_save = 'Battery Low - '+str(battery_percentage)+'%.'

			if device_name.device_name:
				device_name_name = str(device_name.device_name)
			else:
				device_name_name = 'Unknown'

			try:
				report_battery_status = report_instance.battery_status
			except(Exception)as e:
				report_battery_status = None

			if report_battery_status or report_battery_status == None:
				report_obj = {
					"imei":imei,
					"alert_name":'Battery Low',
					"device_name":device_name_name,
					"event_type":"battery",
					"location":address,
					"battery_percentage" : battery_percentage,
					"longitude":longitude,
					"latitude":latitude,
					"type":"alert",
					"speed":speed,
					"notification_sent":True,
					"speed_status":False,
					"battery_status":False,
					"send_notification":send_notification_flag,
					"event": "low"
				}
				report_instance_delete = Reports.objects.filter(event_type='battery', imei=imei).all()
				if report_instance_delete:
					try:
						report_instance_delete.delete()
					except(Exception)as e:
						pass
				_thread.start_new_thread(save_report, (imei, report_obj ))
				_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'battery', global_send_notification_flag))
				# _thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
				_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
				_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
				_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'battery', longitude, latitude))
			else:
				report_obj = {
					"imei":imei,
					"alert_name":'Battery Low',
					"device_name":device_name_name,
					"event_type":"battery",
					"battery_percentage" : battery_percentage,
					"location":address,
					"longitude":longitude,
					"latitude":latitude,
					"type":"alert",
					"speed":speed,
					"notification_sent":False,
					"speed_status":False,
					"battery_status":False
				}

				report_instance_delete = Reports.objects.filter(event_type='battery', imei=imei).all()
				if report_instance_delete:
					try:
						report_instance_delete.delete()
					except(Exception)as e:
						pass

				_thread.start_new_thread(save_report, (imei, report_obj ))
		else:
			if setting_instance.battery_notification:
				# address = get_location(longitude, latitude)
				address = 'Unknown'
				device_name = Subscription.objects.filter(imei_no=imei).last()
				if device_name.device_name:
					message_title = str(device_name.device_name) +' : Battery is above low limit'
				else:
					message_title = 'Battery is above low limit'

				if device_name.device_name:
					message_body = str(device_name.device_name) +' : Battery is above low limit - '+str(battery_percentage)+'%, at '+address+' location.'
				else:
					message_body = 'Battery is above low limit - '+str(battery_percentage)+'%, at '+address+' location.'

				if device_name.device_name:
					device_name_name = str(device_name.device_name)
				else:
					device_name_name = 'Unknown'


				report_obj = {
					"imei":imei,
					"alert_name":'Battery Low',
					"device_name":device_name_name,
					"event_type":"battery",
					"battery_percentage" : battery_percentage,
					"location":address,
					"longitude":longitude,
					"latitude":latitude,
					"type":"alert",
					"speed":speed,
					"notification_sent":False,
					"speed_status":True,
					"battery_status":True
				}
				report_instance_delete = Reports.objects.filter(event_type='battery', imei=imei).all()
				if report_instance_delete:
					try:
						report_instance_delete.delete()
					except(Exception)as e:
						pass
				_thread.start_new_thread(save_report, (imei, report_obj ))

	close_old_connections()
	pass