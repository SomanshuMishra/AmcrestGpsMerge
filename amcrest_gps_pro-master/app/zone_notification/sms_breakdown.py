from twilio.rest import Client
from services.models import *
from app.models import *
from user.models import *
from services.mail_sender import *

from django.db import close_old_connections
from app.sms_service import message_sender, sms_log


# def breakdown_message(imei, customer_id, message, zone_alert, global_sms=False):
# 	if zone_alert and global_sms:
# 		phone_number = ZoneAlert.objects.filter(customer_id=customer_id, id=zone_alert).first()
# 		if phone_number:
# 			if phone_number.phone_one:
# 				if message_sender.send_sms(message, phone_number.phone_one):
# 					sms_log.save_sms_log(imei, customer_id, message)

# 			if phone_number.phone_two:
# 				if message_sender.send_sms(message, phone_number.phone_two):
# 					sms_log.save_sms_log(imei, customer_id, message)
# 	close_old_connections()
# 	pass



def breakdown_message(imei, customer_id, title, message, zone_alert, global_sms=False):
	if zone_alert and global_sms:
		phone_number = ZoneAlert.objects.filter(customer_id=customer_id, id=zone_alert).first()
		if phone_number:
			if phone_number.phone_one:
				if not phone_number.phone_one_mobile_carrier or phone_number.phone_one_mobile_carrier == 'others' or phone_number.phone_one_mobile_carrier == 'Others':
					if message_sender.send_sms(message, phone_number.phone_one):
						sms_log.save_sms_log(imei, customer_id, message)
						message_sender.update_count_sms(customer_id)

				elif phone_number.phone_one_mobile_carrier:
					numbers = [i.lstrip().rstrip() for i in phone_number.phone_one.split(',')]
					numbers = numbers[0]
					domain = MobileServiceProvider.objects.filter(mobile_provider_name=phone_number.phone_one_mobile_carrier).last()
					if domain:
						message_sender.update_count_sms(customer_id)
						numbers = str(numbers)+'@'+domain.mobile_provider_domain
						notification_message_sender([numbers, title, message])
					else:
						if message_sender.send_sms(message, numbers):
							message_sender.update_count_sms(customer_id)
							sms_log.save_sms_log(imei, customer_id, message)

			if phone_number.phone_two:
				if not phone_number.phone_two_mobile_carrier or phone_number.phone_two_mobile_carrier == 'others' or phone_number.phone_two_mobile_carrier == 'Others':
					if message_sender.send_sms(message, phone_number.phone_two):
						sms_log.save_sms_log(imei, customer_id, message)
						message_sender.update_count_sms(customer_id)
				elif phone_number.phone_two_mobile_carrier:
					numbers = [i.lstrip().rstrip() for i in phone_number.phone_two.split(',')]
					numbers = numbers[0]
					domain = MobileServiceProvider.objects.filter(mobile_provider_name=phone_number.phone_two_mobile_carrier).last()
					if domain:
						message_sender.update_count_sms(customer_id)
						numbers = str(numbers)+'@'+domain.mobile_provider_domain
						notification_message_sender([numbers, title, message])
					else:
						if message_sender.send_sms(message, numbers):
							message_sender.update_count_sms(customer_id)
							sms_log.save_sms_log(imei, customer_id, message)
	close_old_connections()
	pass



def breakdown_mail(imei, customer_id, subject, message, zone_alert, global_email=False):
	if zone_alert and global_email:
		mail_id = ZoneAlert.objects.filter(customer_id=customer_id, id=zone_alert).first()
		if mail_id:
			if mail_id.email_one:
				message_sender.send_email(subject, message, mail_id.email_one)
				message_sender.update_count_email(customer_id)

			if mail_id.email_two:
				message_sender.send_email(subject, message, mail_id.email_two)
				message_sender.update_count_email(customer_id)
	close_old_connections()
	pass



def breakdown_obd_message(imei, customer_id, title, message, zone_alert, global_sms=False):
	if zone_alert and global_sms:
		phone_number = ZoneAlertObd.objects.filter(customer_id=customer_id, id=zone_alert).first()
		if phone_number:
			if phone_number.phone_one:
				if not phone_number.phone_one_mobile_carrier or phone_number.phone_one_mobile_carrier == 'others' or phone_number.phone_one_mobile_carrier == 'Others':
					if message_sender.send_sms(message, phone_number.phone_one):
						sms_log.save_sms_log(imei, customer_id, message)
						message_sender.update_count_sms(customer_id)

				elif phone_number.phone_one_mobile_carrier:
					numbers = [i.lstrip().rstrip() for i in phone_number.phone_one.split(',')]
					numbers = numbers[0]
					domain = MobileServiceProvider.objects.filter(mobile_provider_name=phone_number.phone_one_mobile_carrier).last()
					if domain:
						message_sender.update_count_sms(customer_id)
						numbers = str(numbers)+'@'+domain.mobile_provider_domain
						notification_message_sender([numbers, title, message])
					else:
						if message_sender.send_sms(message, numbers):
							message_sender.update_count_sms(customer_id)
							sms_log.save_sms_log(imei, customer_id, message)

			if phone_number.phone_two:
				if not phone_number.phone_two_mobile_carrier or phone_number.phone_two_mobile_carrier == 'others' or phone_number.phone_two_mobile_carrier == 'Others':
					if message_sender.send_sms(message, phone_number.phone_two):
						sms_log.save_sms_log(imei, customer_id, message)
						message_sender.update_count_sms(customer_id)
				elif phone_number.phone_two_mobile_carrier:
					numbers = [i.lstrip().rstrip() for i in phone_number.phone_two.split(',')]
					numbers = numbers[0]
					domain = MobileServiceProvider.objects.filter(mobile_provider_name=phone_number.phone_two_mobile_carrier).last()
					if domain:
						message_sender.update_count_sms(customer_id)
						numbers = str(numbers)+'@'+domain.mobile_provider_domain
						notification_message_sender([numbers, title, message])
					else:
						if message_sender.send_sms(message, numbers):
							message_sender.update_count_sms(customer_id)
							sms_log.save_sms_log(imei, customer_id, message)
	close_old_connections()
	pass



def breakdown_obd_mail(imei, customer_id, subject, message, zone_alert, global_email=False):
	if zone_alert and global_email:
		mail_id = ZoneAlertObd.objects.filter(customer_id=customer_id, id=zone_alert).first()
		if mail_id:
			if mail_id.email_one:
				message_sender.send_email(subject, message, mail_id.email_one)
				message_sender.update_count_email(customer_id)

			if mail_id.email_two:
				message_sender.send_email(subject, message, mail_id.email_two)
				message_sender.update_count_email(customer_id)
	close_old_connections()
	pass