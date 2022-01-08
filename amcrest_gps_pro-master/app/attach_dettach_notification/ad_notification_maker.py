import asyncio
import _thread

from django.conf import settings
from django.db import close_old_connections

from app.models import Subscription, SettingsModel
from app.serializers import ReportsSerializer
from app.notification_saver.notification_saver import *

from .ad_notification_sender import send_notification
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

def attach_notification_receiver(imei, details):
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	args = [imei, longitude, latitude]
	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, attach_notification_sender, args)
	except(Exception)as e:
		pass
	pass


def save_report(imei, details):
	serializer = ReportsSerializer(data=details)
	if serializer.is_valid():
		serializer.save()
	close_old_connections()
	

def attach_notification_sender(args):
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
		send_notification_flag = setting_instance.attach_dettach_notification
	except(Exception) as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.attach_dettach_sms
	except(Exception) as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.attach_dettach_email
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



	query = Q(event_type="attach") | Q(event_type="dettach")
	report_instance = Reports.objects.filter(query, imei=imei).order_by('-id').first()
	try:
		check_event = report_instance.event_type
	except(Exception)as e:
		check_event = None


	if check_event == 'dettach' or check_event == None:
		try:
			address = get_location(longitude, latitude)
		except(Exception)as e:
			print(e)
			address = 'Unknown'

		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = str(device_name_name)+' '+': OBD devcie attached to vehicle port.'
		else:
			message_title = 'OBD devcie attached to vehicle port.'


		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass


		if device_name.device_name:
			message_body = str(device_name_name)+' :'+'OBD Device attached to vehicle port, at '+address+' location. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = str(device_name_name)+' :'+'OBD Device attached to vehicle port, at '+address+' location. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
		else:
			message_body = 'OBD Device attached to vehicle port, at '+address+' location. Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = 'OBD Device attached to vehicle port, at '+address+' location. Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)


		if device_name.device_name:
			message_body_to_save = str(device_name_name)+' :'+'OBD Device attached to vehicle port, at '+address+' location.'
		else:
			message_body_to_save = 'OBD Device attached to vehicle port, at '+address+' location.'


		report_obj = {
			'imei':imei,
			'alert_name':'Attacheds Device to vehicle',
			'device_name':device_name_name,
			'event_type':"attach",
			"location":address,
			"latitude":latitude,
			'longitude':longitude,
			"type":"alert",
			"notification_sent":True,
			"send_notification":send_notification_flag,
			"event": "attach"
		}
		report_instance_delete = Reports.objects.filter(query, imei=imei).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception)as e:
				pass
		_thread.start_new_thread(save_report, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'attach_dettach', global_send_notification_flag))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'attach_dettach', longitude, latitude))
		close_old_connections()
		

	else:
		try:
			address = 'Unknown'
		except(Exception)as e:
			address = 'Unknown'

		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = str(device_name_name)+' '+': OBD devcie attached to vehicle port.'
		else:
			message_title = message_title = 'OBD devcie attached to vehicle port.'

		if device_name.device_name:
			message_body = str(device_name_name)+' :'+'OBD Device attached to vehicle port, at '+address+' location.'
		else:
			message_body = 'OBD Device attached to vehicle port, at '+address+' location.'


		report_obj = {
			'imei':imei,
			'alert_name':'Attached Device to vehicle',
			'device_name':device_name_name,
			'event_type':"attach",
			"location":address,
			"latitude":latitude,
			'longitude':longitude,
			"type":"alert",
			"notification_sent":False,
			"send_notification":True
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


			

def dettach_notification_receiver(imei, details):
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	args = [imei, longitude, latitude]
	
	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, dettach_notification_sender, args)
	except(Exception)as e:
		pass
	pass


def dettach_notification_sender(args):
	imei = args[0]
	try:
		latitude = args[2]
	except(Exception)as e:
		latitude = None

	try:
		longitude = args[1]
	except(Exception)as e:
		longitude = None

	query = Q(event_type="attach") | Q(event_type="dettach")
	report_instance = Reports.objects.filter(query, imei=imei).order_by('-id').first()

	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	
	try:
		send_notification_flag = setting_instance.attach_dettach_notification
	except(Exception) as e:
		send_notification_flag = False

	try:
		send_sms_flag = setting_instance.attach_dettach_sms
	except(Exception) as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.attach_dettach_email
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
	
	try:
		check_event = report_instance.event_type
	except(Exception)as e:
		check_event = None

	
	if check_event == 'attach' or check_event == None:
		try:
			address = get_location(longitude, latitude)
		except(Exception)as e:
			print(e)
			address = 'Unknown'

		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = str(device_name_name)+' '+': OBD devcie dettached from vehicle port.'
		else:
			message_title = 'OBD devcie dettached from vehicle port.'

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass
			
		if device_name.device_name:
			message_body = str(device_name_name)+' :'+'OBD Device dettached from vehicle port, at '+address+' location.'
			message_body_email = str(device_name_name)+' :'+'OBD Device dettached from vehicle port, at '+address+' location.'+NOTE+UNSUBSCRIBE_NOTE
		else:
			message_body = 'OBD Device dettached from vehicle port, at '+address+' location.'
			message_body_email = 'OBD Device dettached from vehicle port, at '+address+' location.'+NOTE+UNSUBSCRIBE_NOTE


		report_obj = {
			'imei':imei,
			'alert_name':'Dettached Device from vehicle port',
			'device_name':device_name_name,
			'event_type':"dettach",
			"location":address,
			"latitude":latitude,
			'longitude':longitude,
			"type":"alert",
			"notification_sent":True,
			"send_notification":True,
			"event": "dettach"
		}
		report_instance_delete = Reports.objects.filter(query, imei=imei).all()
		if report_instance_delete:
			try:
				report_instance_delete.delete()
			except(Exception)as e:
				pass
		_thread.start_new_thread(save_report, (imei, report_obj ))
		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'attach_dettach', global_send_notification_flag))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
		_thread.start_new_thread(save_notifications, (imei, message_title, message_body, device_name.customer_id, report_obj, 'attach_dettach', longitude, latitude))
		close_old_connections()

	else:
		try:
			address = 'Unknown'
		except(Exception)as e:
			address = 'Unknown'

		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		if device_name.device_name:
			message_title = str(device_name_name)+' '+': OBD devcie dettached from vehicle port.'
		else:
			message_title = message_title = 'OBD devcie dettached from vehicle port.'

		if device_name.device_name:
			message_body = str(device_name_name)+' :'+'OBD Device dettached from vehicle port, at '+address+' location.'
		else:
			message_body = 'OBD Device dettached from vehicle port, at '+address+' location.'


		report_obj = {
			'imei':imei,
			'alert_name':'Dettached Device from vehicle port',
			'device_name':device_name_name,
			'event_type':"dettach",
			"location":address,
			"latitude":latitude,
			'longitude':longitude,
			"type":"alert",
			"notification_sent":False,
			"send_notification":True
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