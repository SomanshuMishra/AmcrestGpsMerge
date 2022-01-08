from .models import *
from django.conf import settings
from django.db import close_old_connections
import requests
import json

def get_activation_mail_cc():
	mail_cc = AppConfiguration.objects.filter(key_name='activation_cc_mail').last()
	close_old_connections()
	if mail_cc:
		return mail_cc.key_value
	return settings.ACTIVATION_MAIL_CC


def get_reactivation_mail_cc():
	mail_cc = AppConfiguration.objects.filter(key_name='reactivation_cc_mail').last()
	close_old_connections()
	if mail_cc:
		return mail_cc.key_value
	return settings.REACTIVATION_MAIL_CC


def get_cancellation_mail_cc():
	mail_cc = AppConfiguration.objects.filter(key_name='cancellation_cc_mail').last()
	close_old_connections()
	if mail_cc:
		return mail_cc.key_value
	return settings.CANCELLATION_MAIL_CC


def get_payment_mail_cc():
	mail_cc = AppConfiguration.objects.filter(key_name='payment_update_cc_mail').last()
	close_old_connections()
	if mail_cc:
		return mail_cc.key_value
	return settings.PAYMENT_UPDATE_MAIL_CC


def get_subscription_cancelled_mail_cc():
	mail_cc = AppConfiguration.objects.filter(key_name='subscription_cancelled_mail_cc').last()
	close_old_connections()
	if mail_cc:
		return mail_cc.key_value
	return settings.SUBSCRIPTION_CANCELLED_MAIL_CC


def get_payment_failure_mail_cc():
	mail_cc = AppConfiguration.objects.filter(key_name='payment_failure_mail_cc').last()
	close_old_connections()
	if mail_cc:
		return mail_cc.key_value
	return settings.PAYMENT_FAILURE_MAIL_CC 


def get_subscription_cancel_request_mail_cc():
	mail_cc = AppConfiguration.objects.filter(key_name='subscription_cancel_request_mail_cc').last()
	close_old_connections()
	if mail_cc:
		return mail_cc.key_value
	return settings.SUBSCRIPTION_CANCEL_REQUEST_MAIL_CC 


def get_master_password():
	master_password = AppConfiguration.objects.filter(key_name='master_password').last()
	close_old_connections()
	if master_password:
		return str(master_password.key_value)
	return None


def get_email_domain():
	email_domain = AppConfiguration.objects.filter(key_name='mailgun_email_domain').last()
	close_old_connections()
	if email_domain:
		return str(email_domain.key_value)
	return str(settings.MAILGUN_EMAIL_DOMAIN)


def get_from_email():
	from_email = AppConfiguration.objects.filter(key_name='mailgun_from_email').last()
	close_old_connections()
	if from_email:
		return str(from_email.key_value)
	return settings.MAILGUN_FROM_EMAIL


def get_from_email_notification():
	from_email = AppConfiguration.objects.filter(key_name='mailgun_from_email_notification').last()
	close_old_connections()
	if from_email:
		return str(from_email.key_value)
	return settings.MAILGUN_FROM_EMAIL

def get_mailgun_api_key():
	api_key = AppConfiguration.objects.filter(key_name='mailgun_api_key').last()
	close_old_connections()
	if api_key:
		return str(api_key.key_value)
	return settings.MAILGUN_API_KEY


def get_device_return_mail_cc():
	email = AppConfiguration.objects.filter(key_name='device_return_mail_cc').last()
	close_old_connections()
	if email:
		return email.key_value
	return settings.DEVICE_RETURN_MAIL


def get_notification_sender_email():
	email = AppConfiguration.objects.filter(key_name='get_notification_sender_email').last()
	if email:
		return email.key_value
	return 'noreply@amcrest.com'

def get_pod_sim_message_email():
	email = AppConfiguration.objects.filter(key_name='pod_sim_message_to').last()
	close_old_connections()
	if email:
		return email.key_value
	return settings.POD_SIM_MESSSAGE_TO


def get_error_mail_receiver():
	email = AppConfiguration.objects.filter(key_name='error_mail_receiver').last()
	close_old_connections()
	if email:
		return email.key_value
	return settings.ERROR_MAIL_RECEIVER


def get_pod_username():
	user = AppConfiguration.objects.filter(key_name='pod_user').last()
	if user:
		return user.key_value
	return settings.POD_USER


def get_pod_password():
	password = AppConfiguration.objects.filter(key_name='pod_password').last()
	if password:
		return password.key_value
	return settings.POD_PASSWORD


def get_pod_product_id():
	product_id = AppConfiguration.objects.filter(key_name='pod_product_id').last()
	if product_id:
		return product_id.key_value
	return settings.POD_PRODUCT_ID


def get_pod_token():
	url = "https://api.podiotsuite.com/v3/auth/token"
	payload = "{\n  \"username\": \""+get_pod_username()+"\",\n  \"password\": \""+get_pod_password()+"\"\n}"
	headers = {
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache",
	    }

	response = requests.request("POST", url, data=payload, headers=headers)
	if str(response.status_code) == "200":
		response = response.json()
		return response['token'], response['user']['permissions'][0]['accountId']
	else:
		return None


def get_product_id(token, accountId, iccid):
	url = "https://api.podiotsuite.com/v3/products"

	querystring = {"accountId":accountId,"iccid":iccid}

	headers = {
	    'x-access-token': token,
	    'Cache-Control': "no-cache",
	    }

	response = requests.request("GET", url, headers=headers, params=querystring)
	if str(response.status_code) == "200":
		response = response.json()
		return response[0]['_id']
	else:
		return None


def get_pod_multi_product_id():
	product_id = AppConfiguration.objects.filter(key_name='pod_multi_product_id').last()
	if product_id:
		return product_id.key_value
	return '5d9d10f8a99881002c621d2c'


def get_pod_att_product_id():
	product_id = AppConfiguration.objects.filter(key_name='pod_att_product_id').last()
	if product_id:
		return product_id.key_value
	return '5f2d896823fd370153e6df65'

def get_pod_product_id():
	product_id = AppConfiguration.objects.filter(key_name='pod_product_id').last()
	if product_id:
		return product_id.key_value
	return '5d9d118338c92c0037de7d90'

 
def get_subscriptionId(iccid):
	subscription_id = SimMapping.objects.filter(iccid=iccid).last()
	if subscription_id:
		return subscription_id.subscription_id
	return None