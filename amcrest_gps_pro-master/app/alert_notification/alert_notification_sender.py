import asyncio
import _thread

from pyfcm import FCMNotification

from django.conf import settings
from django.db import close_old_connections

from app.models import NoticationSender, Reports, GoogleMapAPIKey
from app.serializers import ReportsSerializer
from app.notification_saver.notification_saver import *



push_service = FCMNotification(api_key=settings.FCM_NOTIFICATION_API_KEY)



def send_web_notification(args):
	try:
		customer_id = args[3]
	except(Exception)as e:
		customer_id = None

	try:
		report = args[4]
	except(Exception)as e:
		report = {}


	try:
		event_type = args[5]
	except(Exception)as e:
		event_type = 'engine'

	if customer_id:
		web_not = NoticationSender.objects.filter(customer_id=customer_id, category='obd').first()
		if web_not:
			result = push_service.notify_single_device(registration_id=web_not.website, message_title=args[1], message_body=args[2])
			close_old_connections()
	pass


def send_android_notification(args):
	
	try:
		customer_id = args[3]
	except(Exception)as e:
		customer_id = None

	if customer_id:
		web_not = NoticationSender.objects.filter(customer_id=customer_id, category='obd').first()
		if web_not:
			result = push_service.notify_single_device(registration_id=web_not.android, message_title=args[1], message_body=args[2])
			close_old_connections()
		pass
	pass


def send_ios_notification(args):
	print('sending ios send_notification')
	try:
		customer_id = args[3]
	except(Exception)as e:
		customer_id = None

	if customer_id:
		web_not = NoticationSender.objects.filter(customer_id=customer_id, category='obd').first()
		if web_not:
			result = push_service.notify_single_device(registration_id=web_not.ios, message_title=args[1], message_body=args[2])
			close_old_connections()
		pass
	pass

def send_notification(imei, message_title, message_body, customer_id, report, event_type, global_notification):
	args = [imei, message_title, message_body, customer_id, report, event_type]
	print(args, '----------------')
	if report.get('send_notification', None) and global_notification:
		try:
			loop = asyncio.new_event_loop()
			loop.run_in_executor(None, send_web_notification, args)
			print('sent web')
		except(Exception)as e:
			print(e)
			pass

		try:
			loop = asyncio.new_event_loop()
			loop.run_in_executor(None, send_android_notification, args)
		except(Exception)as e:
			pass

		try:
			loop = asyncio.new_event_loop()
			loop.run_in_executor(None, send_ios_notification, args)
		except(Exception)as e:
			pass
	pass
