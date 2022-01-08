import asyncio
import _thread

from datetime import datetime

from django.conf import settings
from django.db import close_old_connections

from app.models import Subscription, SettingsModel
from services.models import DtcRecords
from app.serializers import ReportsSerializer, DtcEventsSerializer
from app.notification_saver.notification_saver import *

from .warning_notification_sender import send_notification
from .location_finder import *
from .sms_breakdown import *

from services.mail_sender import *


#================================Engine Notification============================
def warning_alert_notification_receiver(imei, details):
	args = [imei, details]
	print(args)
	try:
		# alert_notification_sender_function(args)
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, dtc_alert_notification_sender_function, args)
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

# {'protocol': '+RESP:GTOBDTC', 'date': '18/06/2021', 'time': '15:19:11', 'protocol_version': '5E0100', 
# 'imei': '121212121212121', 'warning_code': 'number_of_dtc', 'warning_value': '1', 
# 'warning_details': 'Number of confirmed emission related DTC', 'count_number': '1667', 'send_time': '20210618000945'}

def dtc_alert_notification_sender_function(args):
	imei = args[0]
	details = args[1]

	try:
		setting_instance = SettingsModel.objects.filter(imei=imei).last()
	except(Exception)as e:
		print(e)
		setting_instance= None

	if setting_instance:

		try:
			send_notification_flag = setting_instance.warning_notification
		except(Exception)as e:
			send_notification_flag = False


		try:
			send_sms_flag = setting_instance.warning_sms
		except(Exception)as e:
			send_sms_flag = False

		try:
			send_mail_flag = setting_instance.warning_email
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

		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Warning Detected'
		else:
			message_title = 'Warning Detected'

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : '+details.get('warning_details')+'. On '+date_to_be_send
		else:
			message_body = 'Warning Detected. On '+date_to_be_send

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		report_obj = {
			'imei':imei,
			'customer_id':device_name.customer_id,
			'record_date':time_timezone.date(),
			'record_time':time_timezone.time(),
			'protocol': '+RESP:GTDTC',
			'warning_code': details.get('warning_code'),
			'warning_details': details.get('warning_details'),
			'warning_value': details.get('warning_value'), 
		}

		serializer = ObdDtcEventSerializer(data=report_obj)
		if serializer.is_valid():
			serializer.save()
		else:
			print(serializer.errors)


		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'obd_dtc_warning', global_send_notification_flag))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body, send_mail_flag, global_send_mail_flag))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))