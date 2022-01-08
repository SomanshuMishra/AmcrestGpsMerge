from django.conf import settings
from django.db import close_old_connections
import asyncio
import _thread

from .speed_notification_sender_obd import *
from .speed_location_finder import *
from .sms_breakdown import *

from app.models import Subscription, SettingsModel, Reports
from app.serializers import ReportsSerializer

from app.notification_saver.notification_saver import *

from django.contrib.auth import get_user_model
User = get_user_model()

NOTE = '''<br>
<br>
<b>Note :</b><br>
1. If you are getting more number of emails and you don't want to get such  emails .Then update your settings as written below.<br>
&nbsp;&nbsp;Map ->Click on the device then go to settings->Then in All alerts section you can completely disable your email alerts or you can enable/disable individual section also.
<br>'''



def save_report(imei, details):
	serializers = ReportsSerializer(data=details)
	if serializers.is_valid():
		serializers.save()
	close_old_connections()


def speed_notification_receiver(imei, details):
	longitude = details.get('longitude')
	latitude = details.get('latitude')
	speed = details.get('speed')
	args = [imei, longitude, latitude, speed, details]

	try:
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, speed_notification_maker, args)
	except(Exception)as e:
		print(e)
		pass
	pass

def get_mesurment_unit(imei):
	sub = Subscription.objects.filter(imei_no=imei).last()
	if sub:
		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).last()
		if user:
			return user.uom
		return 'kms'
	return 'kms'

def speed_notification_maker(args):
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
		battery_percentage = details.get('battery_percentage', None)
	except(Exception)as e:
		battery_percentage = None


	setting_instance = SettingsModel.objects.filter(imei=imei).last()
	
	try:
		send_notification_flag = setting_instance.speed_notification
	except(Exception) as e:
		send_notification_flag = False


	try:
		send_sms_flag = setting_instance.speed_sms
	except(Exception) as e:
		send_sms_flag = False

	try:
		send_mail_flag = setting_instance.speed_email
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
		speed_limit = float(setting_instance.speed_limit)
	except(Exception)as e:
		speed_limit = 0

	try:
		if uom == "miles":
			speed_message = str('%.2f'%(speed/1.60934))+' mph.'
		else:
			speed_message = str('%.2f'%speed)+' kmph.'

	except(Exception)as e:
		speed_message = str('%.2f'%speed)+' kmph.'
		print(e)
		
	if speed != 0 and speed != None:
		try:
			# address = get_location(longitude, latitude)
			address = None
		except(Exception)as e:
			address = None

		device_name = Subscription.objects.filter(imei_no=imei).last()

		if device_name.device_name:
			message_title = str(device_name.device_name) +' : Speed Limit Exceeded'
		else:
			message_title = 'Speed Limit Exceeded'

		try:
			UNSUBSCRIBE_NOTE = "<br><a href='https://api.amcrestgps.net/auth/unsubscribe/mail/{}'>To unsubscribe notification mails from Amcrest GPS click here.</a>"
			UNSUBSCRIBE_NOTE = UNSUBSCRIBE_NOTE.format(device_name.customer_id)
		except(Exception)as e:
			pass


		if device_name.device_name:
			message_body_to_save = str(device_name.device_name) +' : Speed Limit Exceeded, speed is '+ speed_message
		else:
			message_body_to_save = 'Speed Limit Exceeded, speed is '+ speed_message

		if device_name.device_name:
			message_body = str(device_name.device_name) +' : Speed Limit Exceeded, speed is '+ speed_message+'.Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = str(device_name.device_name) +' : Speed Limit Exceeded, speed is '+ speed_message+'.Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)
		else:
			message_body = 'Speed Limit Exceeded, speed is '+ speed_message+'.Google Map - https://maps.google.com/?q={},{}'.format(latitude, longitude)
			message_body_email = 'Speed Limit Exceeded, speed is '+ speed_message+'.Google Map - https://maps.google.com/?q={},{}. {}. {}'.format(latitude, longitude, NOTE, UNSUBSCRIBE_NOTE)

		if device_name.device_name:
			device_name_name = str(device_name.device_name)
		else:
			device_name_name = 'Unknown'

		report_obj = {
			"imei":imei,
			"alert_name":'Speed Limit Exceeded',
			"device_name":device_name_name,
			"event_type":"speed",
			"location":address,
			"longitude":longitude,
			"latitude":latitude,
			"type":"alert",
			"speed":speed,
			"notification_sent":True,
			"speed_status":False,
			"send_notification":send_notification_flag,
			"event": "high",
			"battery_percentage":battery_percentage
		}

		try:
			_thread.start_new_thread(send_notification, (imei, message_title, message_body, device_name.customer_id, report_obj, 'speed', global_send_notification_flag))
			_thread.start_new_thread(breakdown_message, (imei, device_name.customer_id, message_title, message_body, send_sms_flag, global_send_sms_flag))
			_thread.start_new_thread(breakdown_mail, (imei, device_name.customer_id, message_title, message_body_email, send_mail_flag, global_send_mail_flag))
			_thread.start_new_thread(save_notifications, (imei, message_title, message_body_to_save, device_name.customer_id, report_obj, 'speed', longitude, latitude))
		except(Exception)as e:
			print(e)
		close_old_connections()