import asyncio
import _thread

from datetime import datetime

from django.conf import settings
from django.db import close_old_connections

from app.models import Subscription, SettingsModel
from services.models import DtcRecords
from app.serializers import ReportsSerializer, DtcEventsSerializer
from app.notification_saver.notification_saver import *

from .dtc_notification_sender import send_notification
from .location_finder import *
from .sms_breakdown import *

from services.mail_sender import *


#================================Engine Notification============================
def dtc_alert_notification_receiver(imei, details):
	args = [imei, details]
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
			from datetime import datetime
			time_zone = get_time_zone(imei)
			time_timezone = datetime.now(pytz.timezone(time_zone))
			date_to_be_send = time_timezone.strftime("%d %B %Y at %I:%M %p")
		except(Exception)as e:
			time_timezone = datetime.now()
			date_to_be_send = time_timezone.strftime("UTC %d %B %Y at %I:%M %p")

		device_name = Subscription.objects.filter(imei_no=imei).last()

		dtc_explanation = DtcRecords.objects.filter(dtc_code=details.get('error_code')).last()

		if not dtc_explanation:
			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Warning Detected'
			else:
				message_title = 'Warning Detected'

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : Warning Detected. On '+date_to_be_send
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
				'dtc_code': details.get('error_code'),
				'dtc_short_description': "https://www.obdiicsu.com/{}.html".format(details.get('error_code')),
				'error_code_url': "https://www.obdiicsu.com/{}.html".format(details.get('error_code')),
				'severity_level': "medium"
			}
			serializer = DtcEventsSerializer(data=report_obj)
			if serializer.is_valid():
				serializer.save()
			else:
				print(serializer.errors)

			subject = 'Error code is not available in database'
			content = 'Error Code :'+details.get('error_code')
			send_error_mail(subject, content)
		else:
			if device_name.device_name:
				message_title = str(device_name.device_name) +' : Warning Detected'
			else:
				message_title = 'Warning Detected'

			if device_name.device_name:
				message_body = str(device_name.device_name) +' : '+details.get('error_code')+' - '+dtc_explanation.dtc_short_description+'. On '+date_to_be_send
			else:
				message_body = details.get('error_code')+' - '+dtc_explanation.dtc_short_description+'. On '+date_to_be_send

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
				'dtc_code': details.get('error_code'),
				'dtc_short_description': dtc_explanation.dtc_short_description,
				'error_code_url': dtc_explanation.error_code_url,
				'severity_level': dtc_explanation.severity_level
			}
			serializer = DtcEventsSerializer(data=report_obj)
			if serializer.is_valid():
				serializer.save()
			else:
				print(serializer.errors)
		_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'dtc_warning', True))
		_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body, True, True))
		_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, True, True))