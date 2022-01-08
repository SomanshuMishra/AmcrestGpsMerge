from twilio.rest import Client
from services.models import *
from app.models import *
from user.models import *
from services.mail_sender import *

from app.sms_service import message_sender, sms_log

from django.contrib.auth import get_user_model
from django.db import close_old_connections



User = get_user_model()


# def breakdown_message(imei, customer_id, message, message_send_flag=False, global_sms=False):
# 	if message_send_flag and global_sms:
# 		phone_number = SettingsModel.objects.filter(imei=imei).last()
# 		if phone_number:
# 			if phone_number.phone:
# 				numbers = [i.lstrip().rstrip() for i in phone_number.phone.split(',')]
# 				if message_sender.send_sms(message, numbers):
# 					sms_log.save_sms_log(imei, customer_id, message)
# 	close_old_connections()
# 	pass



def breakdown_message(imei, customer_id, title, message, message_send_flag=False, global_sms=False):
	if message_send_flag and global_sms:
		phone_number = SettingsModel.objects.filter(imei=imei).last()

		if phone_number:
			if phone_number.phone:
				if not phone_number.mobile_carrier or phone_number.mobile_carrier == 'others' or phone_number.mobile_carrier == 'Others':
					numbers = [i.lstrip().rstrip() for i in phone_number.phone.split(',')]

					if message_sender.send_sms(message, numbers):
						message_sender.update_count_sms(customer_id)
						sms_log.save_sms_log(imei, customer_id, message)
				elif phone_number.mobile_carrier:
					numbers = [i.lstrip().rstrip() for i in phone_number.phone.split(',')]
					numbers = numbers[0]
					domain = MobileServiceProvider.objects.filter(mobile_provider_name=phone_number.mobile_carrier).last()
					if domain:
						message_sender.update_count_sms(customer_id)
						numbers = str(numbers)+'@'+domain.mobile_provider_domain
						notification_message_sender([numbers, title, message])
					else:
						if message_sender.send_sms(message, numbers):
							message_sender.update_count_sms(customer_id)
							sms_log.save_sms_log(imei, customer_id, message)

		if phone_number:
			if phone_number.secondary_phone:
				if not phone_number.secondary_mobile_carrier or phone_number.secondary_mobile_carrier == 'others' or phone_number.secondary_mobile_carrier == 'Others':
					numbers = [i.lstrip().rstrip() for i in phone_number.secondary_phone.split(',')]

					if message_sender.send_sms(message, numbers):
						message_sender.update_count_sms(customer_id)
						sms_log.save_sms_log(imei, customer_id, message)
				elif phone_number.secondary_mobile_carrier:
					numbers = [i.lstrip().rstrip() for i in phone_number.secondary_phone.split(',')]
					numbers = numbers[0]
					domain = MobileServiceProvider.objects.filter(mobile_provider_name=phone_number.secondary_mobile_carrier).last()
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


def breakdown_mail(imei, customer_id, subject, message, mail_send_flag=False, global_email=False):
	if mail_send_flag and global_email:
		mail_id = SettingsModel.objects.filter(imei=imei).last()
		if mail_id:
			if mail_id.email:
				mails = [i.lstrip().rstrip() for i in mail_id.email.split(',')]
				message_sender.update_count_email(customer_id)
				message_sender.send_email(subject, message, mails)
	close_old_connections()
	pass