from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string

import requests
import asyncio

from user.models import *
from user.serializers import *

from app.serializers import *
from app.models import *

from services.models import *
from services.serializers import *
from services.sim_update_service import *
from services.helper import *



def get_user(user_id):
    user = User.objects.filter(id=user_id).first()
    serializer = UserSerialzer(user)
    return serializer.data

def get_user_from_customerId(customer_id):
    user = User.objects.filter(customer_id=customer_id, subuser=False).first()
    serializer = UserSerialzer(user)
    return serializer.data

def get_model_name(category):
	categories = SimMapping.objects.filter(category=category).values('model').distinct()
	category_list = [i.get('model') for i in categories]
	return category_list

def get_subscription_details(customer_id):
    subscription_instance = Subscription.objects.filter(customer_id=customer_id, is_active=True).all()
    serializer = SubscriptionSerializer(subscription_instance, many=True)
    return serializer.data


def get_resend_subscription_details(customer_id, category_list):
	subscription_instance = Subscription.objects.filter(customer_id=customer_id, device_in_use=True, device_listing=True, device_model__in=category_list).all()
	serializer = SubscriptionSerializer(subscription_instance, many=True)
	return serializer.data

def get_subscription_details_by_id(sub_id):
	subscription_instance = Subscription.objects.filter(subscription_id=sub_id).last()
	serializer = SubscriptionSerializer(subscription_instance)
	return serializer.data


def get_device_category(imei):
	sim_mapping = SimMapping.objects.filter(imei=imei).last()
	if sim_mapping:
		return sim_mapping.category
	return 'gps'


def get_registration_request_emails():
	mails = AppConfiguration.objects.filter(key_name='request_registration_email').last()
	if mails:
		if mails.key_value:
			mails_list = mails.key_value.split(",")
			return mails_list
		return []
	return []

def resend_registration_mail(args):
	user_id = args[0]
	host = args[1]
	password = args[2]
	category = args[3]
	user_details = get_user(user_id)
	category_list = get_model_name(category)
	subscriptions = get_resend_subscription_details(user_details['customer_id'], category_list)


	try:
		if category == 'obd':
			plaintext = get_template('subscribe_devices.txt')
			text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
			rendered = render_to_string('resend_activation_mail_obd.html', {'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
		else:
			plaintext = get_template('subscribe_devices.txt')
			text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
			rendered = render_to_string('resend_activation_mail.html', {'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
	except(Exception)as e:
		print(e)

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_activation_mail_cc(),
              "subject": "Your GPS Tracker is Now Active!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass

def send_registration_mail(args):
	user_id = args[0]
	host = args[1]
	password = args[2]

	user_details = get_user(user_id)
	subscriptions = get_subscription_details(user_details['customer_id'])
	category = get_device_category(subscriptions[0].get('imei_no'))
	if category == 'obd':
		plaintext = get_template('user_registration_obd.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
		rendered = render_to_string('user_registration_obd.html', {'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
	else:
		plaintext = get_template('user_registration.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
		rendered = render_to_string('user_registration.html', {'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})


	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_activation_mail_cc(),
              "subject": "Your GPS Tracker is Now Active!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


	if category != 'obd':
		rendered = render_to_string('user_guid.html')
		text_content = 'How to get the best from your Amcrest GPS Tracker.'

		try:
			res = requests.post(
	        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
	        auth=("api", get_mailgun_api_key()),
	        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
	              "to": [user_details['emailing_address']],
	              "subject": "How to get the best from your Amcrest GPS Tracker.",
	              "text": text_content,
	              "html": rendered
	              })
		except(Exception)as e:
			print(e, 'error during sending mail')
			pass


def send_dealer_registration_mail(args):
	user_id = args[0]
	host = args[1]
	password = args[2]

	user_details = get_user(user_id)
	subscriptions = get_subscription_details(user_details['customer_id'])
	category = get_device_category(subscriptions[0].get('imei_no'))

	if category == 'obd':
		plaintext = get_template('user_registration_obd.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
		rendered = render_to_string('dealer_registration_obd.html', {'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
	else:
		plaintext = get_template('user_registration.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
		rendered = render_to_string('dealer_registration.html', {'subscription': subscriptions, 'user':user_details, 'host':host, 'password':password})
	
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_activation_mail_cc(),
              "subject": "Your GPS Tracker is Now Active!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_subscription_mail(args):
	user_id = args[0]
	host = args[1]
	subscriptions = args[2]
	category = get_device_category(subscriptions[0].get('imei_no'))
	user_details = get_user(user_id)

	if category == 'obd':
		plaintext = get_template('subscribe_devices_obd.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('subscribe_devices_obd.html', {'subscription': subscriptions, 'user':user_details, 'host':host})
	else:
		plaintext = get_template('subscribe_devices.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('subscribe_devices.html', {'subscription': subscriptions, 'user':user_details, 'host':host})


	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_activation_mail_cc(),
              "subject": "Your GPS Tracker is Now Active!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def send_request_mail(args):
	data = args[0]
	
	data = json.dumps(data)
	rendered = '<div>'+data+'</div>'
	text_content = data
	to_mail = get_registration_request_emails()
	# print(to_mail)
	if to_mail:
		try:
			res = requests.post(
	        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
	        auth=("api", get_mailgun_api_key()),
	        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
	              "to": to_mail,
	              "subject": "Registration Request on API amcrestgps.net",
	              "text": text_content,
	              "html": rendered
	              })
		except(Exception)as e:
			print(e, 'error during sending mail')
			pass
	else:
		print(';ff')
	pass


def send_update_request_mail(args):
	data = args[0]
	
	data = json.dumps(data)
	rendered = '<div>'+data+'</div>'
	text_content = data
	# print(rendered)
	if text_content:
		try:
			res = requests.post(
	        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
	        auth=("api", get_mailgun_api_key()),
	        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
	              "to": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
	              "subject": "Amcrest GPS - Update Plan",
	              "text": text_content,
	              "html": rendered
	              })
			print('send email')
		except(Exception)as e:
			print(e, 'error during sending mail')
			pass
	else:
		print(';ff')
	pass


def send_dealer_subscription_mail(args):
	user_id = args[0]
	host = args[1]
	subscriptions = args[2]
	category = get_device_category(subscriptions[0].get('imei_no'))
	user_details = get_user(user_id)

	if category == 'obd':
		plaintext = get_template('subscribe_devices_obd.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('subscribe_dealer_devices_obd.html', {'subscription': subscriptions, 'user':user_details, 'host':host})
	else:
		plaintext = get_template('subscribe_devices.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('subscribe_dealer_devices.html', {'subscription': subscriptions, 'user':user_details, 'host':host})


	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_activation_mail_cc(),
              "subject": "Your GPS Tracker is Now Active!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass






def send_cancellation_mail(args):
	user_id = args[0]
	host = args[1]
	sub_id = args[2]
	user_details = get_user(user_id)
	subscriptions = get_subscription_details_by_id(sub_id)

	category = get_device_category(subscriptions.get('imei_no', None))

	if category == 'obd':
		plaintext = get_template('cancellation_obd.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('cancellation_obd.html', {'subscription': subscriptions, 'user':user_details, 'host':host})
	else:
		plaintext = get_template('cancellation.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('cancellation.html', {'subscription': subscriptions, 'user':user_details, 'host':host})


	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_cancellation_mail_cc(),
              "subject": "Cancelled Subscription!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def forgot_password_mail(args):
	email = args[0]
	reset_link = args[1]
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "subject": "Reset Password Request.",
              "text": 'Reset Password Request.',
              "html": '<p>You have requested for reset password, please click on the link to reset password.</p></br><p>To reset password <a href="'+reset_link+'">Click Here</a></p>'
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_reactivation_mail(args):
	user_id = args[0]
	host = args[1]
	sub_id = args[2]
	user_details = get_user(user_id)
	subscriptions = get_subscription_details_by_id(sub_id)

	category = get_device_category(subscriptions.get('imei_no', None))

	if category == 'obd':
		plaintext = get_template('reactivation_obd.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('reactivation_obd.html', {'subscription': subscriptions, 'user':user_details, 'host':host})
	else:
		plaintext = get_template('reactivation.txt')
		text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
		rendered = render_to_string('reactivation.html', {'subscription': subscriptions, 'user':user_details, 'host':host})

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_reactivation_mail_cc(),
              "subject": "Your GPS tracker has been reactivated!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass

def send_payment_update_mail(args):
	user_id = args[0]
	host = args[1]
	sub_id = args[2]
	user_details = get_user(user_id)
	subscriptions = get_subscription_details_by_id(sub_id)

	plaintext = get_template('service_plan.txt')
	text_content = plaintext.render({'subscription': subscriptions, 'user':user_details, 'host':host})
	rendered = render_to_string('service_plan.html', {'subscription': subscriptions, 'user':user_details, 'host':host})

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_reactivation_mail_cc(),
              "subject": "Your Device Plan Updated!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass

def payment_update_mail(args):
	user_id = args[0]
	host = args[1]
	card = args[2]

	user_details = get_user(user_id)

	plaintext = get_template('payment.txt')
	text_content = plaintext.render({'card': card, 'user':user_details, 'host':host})
	rendered = render_to_string('payment.html', {'card': card, 'user':user_details, 'host':host})

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_payment_mail_cc(),
              "subject": "Payment Account Update!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def subscription_cancel_mail(args):
	imei = args[0]
	email = args[1]
	host = args[2]
	customer_id = args[3]

	category = get_device_category(imei)

	if category == 'obd':
		plaintext = get_template('submission_cancelled_obd.txt')
		text_content = plaintext.render({'imei': imei})
		rendered = render_to_string('submission_cancelled_obd.html', {'imei': imei, 'customer_id':customer_id, 'host':host})
	else:
		plaintext = get_template('submission_cancelled.txt')
		text_content = plaintext.render({'imei': imei})
		rendered = render_to_string('submission_cancelled.html', {'imei': imei, 'customer_id':customer_id, 'host':host})

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "bcc": get_subscription_cancelled_mail_cc(),
              "subject": "Subscription Cancelled!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def payment_failure_mail(args):
	email = args[0]
	host = args[1]
	customer_id =args[2]
	imei = args[3]

	plaintext = get_template('payment_failure.txt')
	text_content = plaintext.render({'customer_id': customer_id})
	rendered = render_to_string('payment_failure.html', {'customer_id':customer_id, 'host':host, 'imei':imei})

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "bcc": get_payment_failure_mail_cc(),
              "subject": "Failed Payment Method!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def subscription_cancel_request_mail(args):
	user_id = args[0]
	host = args[1]
	customer_id = args[2]
	data = args[3]
	user = args[4]

	category = get_device_category(data.get('imei_no'))

	if category == 'obd':
		user_details = get_user(user_id)
		plaintext = get_template('subscription_cancel_request_obd.txt')
		text_content = plaintext.render({'customer_id': customer_id})
		rendered = render_to_string('subscription_cancel_request_obd.html', {'customer_id':customer_id, 'host':host, 'data':data, 'user':user})
	else:
		user_details = get_user(user_id)
		plaintext = get_template('subscription_cancel_request.txt')
		text_content = plaintext.render({'customer_id': customer_id})
		rendered = render_to_string('subscription_cancel_request.html', {'customer_id':customer_id, 'host':host, 'data':data, 'user':user})

	

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_subscription_cancel_request_mail_cc(),
              "subject": "Subscription Cancel request!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def device_return_mail(args):
	user_id = args[0]
	host = args[1]
	customer_id =args[2]
	data = args[3]
	user = args[4]

	user_details = get_user(user_id)
	plaintext = get_template('device_return.txt')
	text_content = plaintext.render({'customer_id': customer_id})
	rendered = render_to_string('device_return.html', {'customer_id':customer_id, 'host':host, 'data':data, 'user':user})

	

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_details['emailing_address']],
              "bcc": get_device_return_mail_cc(),
              "subject": "Subscription Cancelled/Returned!",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def pod_sim_message_email(args):
	iccid = args[0]
	plan_id = args[1]
	subscription = Subscription.objects.filter(imei_iccid=iccid).last()
	if subscription:
		plaintext = get_template('pod_sim_message.txt')
		text_content = plaintext.render({'customer_id': subscription.customer_id})
		rendered = render_to_string('pod_sim_message.html', {'customer_id':subscription.customer_id, 'iccid':iccid, 'plan_id':plan_id})

		try:
			res = requests.post(
	        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
	        auth=("api", get_mailgun_api_key()),
	        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
	              "to": [get_pod_sim_message_email()],
	              "subject": "Amcrest GPS Tracking - New Customer Onboard, activate sim!",
	              "text": text_content,
	              "html": rendered
	              })
		except(Exception)as e:
			print(e, 'error during sending mail')
			pass


def pod_sim_device_message_email(args):
	iccid = args[0]
	message = args[1]
	
	plaintext = get_template('pod_sim_device_message.txt')
	text_content = plaintext.render({'iccid': iccid, 'message':message})
	rendered = render_to_string('pod_sim_device_message.html', {'message':message, 'iccid':iccid})

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [get_pod_sim_message_email()],
              "subject": "Amcrest GPS Tracking - Send Message to POD sim",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def pod_sim_odometer_message_email(args):
	iccid = args[0]
	message = args[1]
	sim_mapping = SimMapping.objects.filter(iccid=iccid).last()
	if sim_mapping:
		rendered = render_to_string('pod_sim_odometer_message.html', {'imei':sim_mapping.imei, 'iccid':iccid, 'message':message})

		try:
			res = requests.post(
	        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
	        auth=("api", get_mailgun_api_key()),
	        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
	              "to": [get_pod_sim_message_email()],
	              "subject": "Amcrest GPS Tracking - Update Odometer!",
	              "html": rendered
	              })
		except(Exception)as e:
			print(e, 'error during sending mail')
			pass


def pod_sim_frequency_email(args):
	iccid = args[0]
	plan_id = args[1]
	subscription = Subscription.objects.filter(imei_iccid=iccid).last()
	if subscription:
		plaintext = get_template('device_frequency.txt')
		text_content = plaintext.render({'customer_id': subscription.customer_id})
		rendered = render_to_string('device_frequency.html', {'customer_id':subscription.customer_id, 'iccid':iccid, 'plan_id':plan_id})

		try:
			res = requests.post(
	        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
	        auth=("api", get_mailgun_api_key()),
	        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
	              "to": [get_pod_sim_message_email()],
	              "subject": "Amcrest GPS Tracking - Device Frequency Update!",
	              "text": text_content,
	              "html": rendered
	              })
		except(Exception)as e:
			print(e, 'error during sending mail')
			pass


def send_error_mail(subject, content):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [get_error_mail_receiver()],
              "subject": subject,
              "text": content
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def send_device_reporting_mail(subject, content):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": ['mayur.patil1211@gmail.com', 'santosh@amcrest.com', 'piyusht189@gmail.com', 'mraswinipanigrahi@gmail.com'],
              "subject": subject,
              "text": content
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_information_mail(subject, content):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [get_error_mail_receiver()],
              "subject": subject,
              "text": content
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass

def send_information_mail_async(args):
	subject = args[0]
	content = args[1]
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [get_error_mail_receiver()],
              "subject": subject,
              "text": content
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def send_cron_mail(imei_list):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [get_error_mail_receiver()],
              # "to": ['mayur.patil1211@gmail.com'],
              "subject": 'Cron Info',
              "text": 'Cron Running '+imei_list
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_cron_mail_24(imei_list):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [get_error_mail_receiver()],
              # "to": ['mayur.patil1211@gmail.com'],
              "subject": '24 hour Cron Info',
              "text": '24 hour Cron Running ' + imei_list
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass

def send_cron_mail_fuel_economy(imei_list):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              # "to": [get_error_mail_receiver(), 'mayur.patil1211@gmail.com'],
              "to": ['mayur.patil1211@gmail.com', 'santosh@amcrest.com'],
              "subject": 'Fuel Economy Cron Running',
              "text": 'Fuel Economy Cron Running ' + imei_list
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def featured_trip(from_, to):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": ['mayur.patil1211@gmail.com'],
              # "to": ['mayur.patil1211@gmail.com'],
              "subject": 'Copying Data',
              "text": 'Copying Data {} to {}'.format(str(from_), str(to))
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_device_listing_cron_mail(imei_list):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [get_error_mail_receiver()],
              # "to": ['mayur.patil1211@gmail.com'],
              "subject": 'Device Listing Cron',
              "text": 'Device Listing Cron, ICCID to be deactivated ' + imei_list
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass




def enquiry_mail(args):
	customer_id = args[0]
	imei = args[1]
	message =args[2]
	category = args[3]

	user = get_user_from_customerId(customer_id)

	if user:
		if user.get('is_dealer_user'):
			customer_user = DealerCustomers.objects.filter(customer=user.get('id')).last()
			if customer_user:
				to_email = customer_user.dealer.email
			else:
				to_email = None
		else:
			to_email = None

		
		plaintext = get_template('enquiry.txt')
		text_content = plaintext.render({'customer_id': customer_id})
		rendered = render_to_string('enquiry.html', {'customer_id':customer_id, 'imei':imei, 'message':message, 'category':category, 'name':user['first_name']+' '+user['last_name'], 'email':user['email']})

		# print(rendered)

		if category == 'obd':
			subject = "GPS Fleet Support: {0} {1}".format(user['first_name']+' '+user['last_name'], imei)
		else:
			subject = "GPS Support: {0} {1}".format(user['first_name']+' '+user['last_name'], imei)

		try:
			if to_email:
				res = requests.post(
		        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
		        auth=("api", get_mailgun_api_key()),
		        data={"from": user['email'],
		              "to": [to_email],
		              # "bcc": get_device_return_mail_cc(),
		              "subject": subject,
		              "text": text_content,
		              "html": rendered
		              })
			else:
				res = requests.post(
		        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
		        auth=("api", get_mailgun_api_key()),
		        data={"from": user['email'],
		              "to": ['amcrestgpssupport@amcrest.com'],
		              # "bcc": get_device_return_mail_cc(),
		              "subject": subject,
		              "text": text_content,
		              "html": rendered
		              })
		except(Exception)as e:
			print(e, 'error during sending mail')
			pass



def device_not_reporting_mail(args):
	email = args[0]
	imei = args[1]
	
	plaintext = get_template('device_not_reporting_gps.txt')
	text_content = plaintext.render({'imei': imei})
	rendered = render_to_string('device_not_reporting_gps.html', {'imei':imei})

	# print(rendered)
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              # "bcc": get_device_return_mail_cc(),
              "subject": "GPS Support: Device Not Reported",
              "text": text_content,
              "html": rendered
              })
		print(res.text, '000')
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def registered_not_loggedin_mail(args):
	email = args[0]
	
	plaintext = get_template('registered_not_loggedin.txt')
	text_content = plaintext.render({'email': email})
	rendered = render_to_string('registered_not_loggedin.html', {'email':email})

	# print(rendered)
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "bcc": get_device_return_mail_cc(),
              "subject": "Login Reminder",
              "text": text_content,
              "html": rendered
              })
		print(res.text, '000')
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def review_mail(args):
	email = args[0]
	customer_id = args[1]
	fname = args[2]
	lname = args[3]
	
	# plaintext = get_template('registered_not_loggedin.txt')
	# text_content = plaintext.render({'email': email})
	rendered = render_to_string('review.html', {'email':email, 'fname':fname, 'lname':lname})

	text_content = 'Review Mail'
	# rendered = '<h1>Review Mail From amcrestgps.com</h1>'

	# print(rendered)
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "bcc": get_device_return_mail_cc(),
              "subject": "Sincere Request from Amcrest GPS Tracker",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def review_rating_less(args):
	customer_id = args[0]
	comments = args[1]
	user = get_user_from_customerId(customer_id)
	rating = args[2]
	
	# plaintext = get_template('registered_not_loggedin.txt')
	# text_content = plaintext.render({'email': email})
	# rendered = render_to_string('review.html', {'email':email})

	text_content = 'Review Mail'
	rendered = '<b>Content : </b>User with customer id - {0} has submitted the  following feedback. \
				<br>\
				<b>Comments :</b>{1}<br>\
				<b>Rating :</b>{2}<br>'.format(customer_id, comments, rating)
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": user.get('email', None),
              "to": ['amcrestgpssupport@amcrest.com'],
              "bcc": get_device_return_mail_cc(),
              "subject": "Review Popup Amcrestgps.net",
              "text": text_content,
              "html": rendered
              })
		print(res.text, '000')
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass




def review_rating_more(args):
	customer_id = args[0]
	comments = args[1]
	user = get_user_from_customerId(customer_id)
	rating = args[2]
	
	# plaintext = get_template('registered_not_loggedin.txt')
	# text_content = plaintext.render({'email': email})
	# rendered = render_to_string('review.html', {'email':email})

	text_content = 'Review Mail'
	rendered = '<b>Content : </b>User with customer id - {0} has submitted the  following feedback. \
				<br>\
				<b>Comments :</b>{1}<br>\
				<b>Rating :</b>{2}<br>'.format(customer_id, comments, rating)
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": user.get('email', None),
              "to": ['santosh@amcrest.com'],
              "bcc": get_device_return_mail_cc(),
              "subject": "Review Popup Amcrestgps.net",
              "text": text_content,
              "html": rendered
              })
		# print(res.text, '000')
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass

def notification_message_sender(args):
	to = args[0]
	title = args[1]
	message = args[2]

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_notification_sender_email()+'>',
              "to": [to],
              "subject": title,
              "text": message,
              "html": message
              })
		# print(res.text, '000')
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def unsubscribed_mail(args):
	customer_id = args[0]
	user = get_user_from_customerId(customer_id)
	rendered = '<!DOCTYPE html><html lang="en"><head><title>Amcrest GPS</title></head><body><div style="text-align: center;"><h2>"You have unsubscribed the mail from amcrest gps"</h2>\
	</div><p style="text-align: center;color: #076ba6;">Note : To subscribe again go to settings-> enable the email.</p></body></html>'
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS<amcrestgpssupport@amcrest.com>',
              "to": user.get('email', None),
              "subject": 'Unsubscribe mail at Amcrest GPS',
              "text": 'Mail Unsubscribed',
              "html": rendered
              })
		print(res.text, '000')
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def dataflush_mail():
	rendered = '<!DOCTYPE html><html lang="en"><head><title>Amcrest GPS</title></head><body><h1>Data Flush Cron Running</h1></body></html>'
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS<amcrestgpssupport@amcrest.com>',
              "to": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "subject": 'Data Flush',
              "text": 'Data Flush',
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def daily_pod_sim_cron(imei_list):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              # "to": [get_error_mail_receiver()],
              "to": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "subject": 'Pod Sim Deactivate Cron',
              "text": 'Pod Sim Deactivate Cron, ICCID to be deactivated ' + imei_list
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def cron_mail_sender(subject, message):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              # "to": [get_error_mail_receiver()],
              "to": ['mayur.patil1211@gmail.com'],
              "subject": subject,
              "text": message
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def data_backup_cron_mail_sender(subject, message):
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              # "to": [get_error_mail_receiver()],
              "to": ['mayur.patil1211@gmail.com', 'santosh@amcrest.com'],
              "subject": subject,
              "text": message
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def positive_feedback_mail_sender(email, data):
	text_content = 'Amcrest Feedback'
	rendered = render_to_string('positive_feedback.html', data)
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "subject": 'Free 1 Months of Amcrest GPS Subscription Applied to your account',
              "bcc": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def negative_feedback_mail_sender(email, data):
	text_content = 'Amcrest Feedback'
	rendered = render_to_string('negative_feedback.html', data)
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "subject": 'Free 1 Months of Amcrest GPS Subscription Applied to your account',
              "bcc": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def negative_feedback_support_mail(email, data):
	text_content = 'Amcrest Feedback'
	rendered = '<b>Name : </b> {0} {1}. \
				<br>\
				<b>email :</b>{2}<br>\
				<b>Improve Softwares :</b>{3}<br>\
				<b>Missing Features :</b>{4}<br>\
				<b>Additional Information :</b>{5}<br>\
				<b>Rating :</b>{6}<br>'.format(data.get('first_name', ''), data.get('last_name', ''), data.get('email', ''), data.get('improve_software', ''), data.get('missing_features', ''), data.get('additional_information', ''), data.get('rating', ''))

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": ['amcrestgpssupport@amcrest.com'],
              "subject": 'Feedback from customer',
              "bcc": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass



def send_gps_invoice_mail(email, file_path):
	text_content = 'Please find your invoice in attachment.'
	rendered = '<p>Please find your invoice in attachment.</p>'
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        files=[("attachment", ("invoice.pdf", open(file_path,"rb").read()))],
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              # "bcc": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "subject": "Amcrest GPS Pro subscription invoice",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_obd_invoice_mail(email, file_path):
	text_content = 'Please find your invoice in attachment.'
	rendered = '<p>Please find your invoice in attachment.</p>'
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        files=[("attachment", ("invoice.pdf", open(file_path,"rb").read()))],
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              # "bcc": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "subject": "Amcrest GPS Fleet subscription invoice",
              "text": text_content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_mail_from_support(email, subject, content):
	rendered = '<p>'+content+'</p>'
	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [email],
              "subject": subject,
              "text": content,
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


def send_free_trial_mail(customer_id, next_billing_date, duration):
	text_content = 'Amcrest Free Trial'
	user_d = get_user_from_cuget_from_emailstomerId(customer_id)
	rendered = render_to_string('free_trial.html', {'first_name':user_d.get('first_name'), 'last_name':user_d.get('last_name'), 'nextBillingDate':next_billing_date, 'duration':duration})

	try:
		res = requests.post(
        "https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
        auth=("api", get_mailgun_api_key()),
        data={"from": 'Amcrest GPS <'+get_from_email()+'>',
              "to": [user_d.get('emailing_address')],
              "bcc": ['santosh@amcrest.com', 'mayur.patil1211@gmail.com'],
              "subject": 'Free {} Months of Amcrest GPS Subscription Applied to your account'.format(str(duration)),
              "text": 'Free {} Months of Amcrest GPS Subscription Applied to your account'.format(str(duration)),
              "html": rendered
              })
	except(Exception)as e:
		print(e, 'error during sending mail')
		pass


import json
def send_batch_message(subject, content):
	rendered = '<p>'+content+'</p>'
	
	count = round(User.objects.filter(is_active=True).count()/500) + 1
	till = 499
	start = 0
	for i in range(count):
		decti = {}
		user = User.objects.filter(is_active=True, subuser=False)[start:till]
		to_mail = [i.emailing_address for i in user]
		for i in user:
			decti[i.emailing_address] = {
				"id":i.id,
				"first":i.first_name
			}

		if to_mail:
			res = requests.post(
			"https://api.mailgun.net/v3/"+get_email_domain()+"/messages",
			auth=("api", get_mailgun_api_key()),
			data={"from": 'Amcrest GPS <'+get_from_email()+'>',
					"to": to_mail,
					"subject": subject,
					"text": content,
					"html": rendered,
					"recipient-variables": (json.dumps(decti))})
		start = till+1
		till = till + 500
	return True