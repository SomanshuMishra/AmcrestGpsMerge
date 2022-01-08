from twilio.rest import Client
from django.conf import settings
from django.db import close_old_connections

from services.models import *
from app.models import *
from user.models import *
from services.helper import *
import requests
import datetime



def get_twilio_sid():
	app_conf = AppConfiguration.objects.filter(key_name='twilio_sid').first()
	close_old_connections()
	if app_conf:
		return app_conf.key_value
	return settings.TWILIO_SID


def get_twilio_token():
	app_conf = AppConfiguration.objects.filter(key_name='twilio_token').first()
	close_old_connections()
	if app_conf:
		return app_conf.key_value
	return settings.TWILIO_TOKEN


def get_twilio_from_number():
	app_conf = AppConfiguration.objects.filter(key_name='twilio_from_number').first()
	close_old_connections()
	if app_conf:
		return app_conf.key_value
	return settings.TWILIO_FROM_NUMBER

def send_sms(message_body, number):
	client = Client(get_twilio_sid(), get_twilio_token())
	# client = Client("AC7f0106ada2e3c2f8f745f6b2c4752f47", "d18c56acfa4ddf441faf0ef8564453d4")
	# print(number)
	message = client.messages.create(
			to = number,
			from_ = get_twilio_from_number(),
			body = message_body
		)
	# print(message)
	if not message.error_code:
		return True
	return False


def send_email(subject, message, mail_id):
	try:
		# print(mail_id)
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": mail_id,
              "subject": subject,
              "text": message,
              "html": message
              })
		# print(res.text)
	except(Exception)as e:
		print(e)
		pass



def update_count_sms(customer_id):
	count = SmsEmailCount.objects.filter(customer_id=customer_id, record_date=datetime.datetime.now().date()).last()
	if count:
		if count.sms_count:
			count.sms_count = count.sms_count+1 
			count.save()
		else:
			count.sms_count = 1 
			count.save()
	else:
		save_count = SmsEmailCount(
				customer_id=customer_id,
				sms_count = 1
			)
		save_count.save()


def update_count_email(customer_id):
	count = SmsEmailCount.objects.filter(customer_id=customer_id, record_date=datetime.datetime.now().date()).last()
	if count:
		if count.email_count:
			count.email_count = count.email_count+1 
			count.save()
		else:
			count.email_count = 1
			count.save()
	else:
		save_count = SmsEmailCount(
				customer_id=customer_id,
				sms_count = 1
			)
		save_count.save()