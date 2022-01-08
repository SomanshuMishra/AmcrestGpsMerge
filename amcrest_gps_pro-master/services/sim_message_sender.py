from app.models import *
from services.models import *
from services.serializers import *
from services.mail_sender import *
from services.helper import *

from django.db import close_old_connections

import requests
import base64
import asyncio



def activate_sim_list(imei_list, plan_id, send_message_flag):
	for imei in imei_list:
		args = [imei, plan_id, send_message_flag]
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, sim_activate_requests, args)

	# for imei in imei_list:
	# 	args = [imei]
	# 	loop = asyncio.new_event_loop()
	# 	loop.run_in_executor(None, send_message_restrict_inf, args)



def send_message_restrict_inf(args):
	imei = args[0]
	if imei:
		sim_iccid = SimMapping.objects.filter(imei=imei).first()
		message_to_send = 'AT+GTCFG=gl300m,,gl300m,,,,,,,,,,,0,,,,,,,,FFFF$'
		if sim_iccid:
			if sim_iccid.provider == 'pod':
				status = send_message_pod_module(sim_iccid.iccid, message_to_send, sim_iccid.model)
				return status
			elif sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
				status = send_message_pod_multi_module(sim_iccid.iccid, message_to_send, sim_iccid.model)
				return status
		else:
			pass
	else:
		pass

def message_receiver(imei, message):
	sim_iccid = SimMapping.objects.filter(imei=imei).first()
	save_command(imei, message)
	if sim_iccid:
		if sim_iccid.provider == 'tele2':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
			close_old_connections()
			if sim_cred:
				_auth = sim_cred.username+':'+sim_cred.api_key
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			else:
				_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)

			status = send_message_tele_module(sim_iccid.iccid, auth, message, sim_iccid.model)
			return status
		elif sim_iccid.provider == 'pod':
			status = send_message_pod_module(sim_iccid.iccid, message, sim_iccid.model)
			return status
		elif sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
			status = send_message_pod_multi_module(sim_iccid.iccid, message, sim_iccid.model)
			return status


def message_receiver_reboot(imei, message):
	sim_iccid = SimMapping.objects.filter(imei=imei).first()
	# save_command(imei, message)
	if sim_iccid:
		if sim_iccid.provider == 'tele2':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
			close_old_connections()
			if sim_cred:
				_auth = sim_cred.username+':'+sim_cred.api_key
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			else:
				_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)

			status = send_message_tele_module(sim_iccid.iccid, auth, message, sim_iccid.model)
			return status
		elif sim_iccid.provider == 'pod':
			status = send_message_pod_module(sim_iccid.iccid, message, sim_iccid.model)
			return status
		elif sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
			status = send_message_pod_multi_module(sim_iccid.iccid, message, sim_iccid.model)
			return status


def save_command(imei, message):
	if message:
		serializer = DeviceCommandsSerializer(data={'imei':imei, 'command':message})
		if serializer.is_valid():
			serializer.save()
		else:
			device_commands = DeviceCommands(
				imei=imei,
				command = message
				)
			device_commands.save()
		return True
	else:
		subject = 'Error during saving command, please look into the app configuration table. Or please save into table'
		content = 'imei :'+imei+',\n\n Message : '+message
		send_error_mail(subject, content)
		return False

def send_message_listener(imei):
	sim_iccid = SimMapping.objects.filter(imei=imei).first()
	if sim_iccid:
		message_key = sim_iccid.model+'_listener'
		app_conf = AppConfiguration.objects.filter(key_name=message_key).first()
		if app_conf:
			if sim_iccid.provider == 'tele2':
				sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
				close_old_connections()
				if sim_cred:
					_auth = sim_cred.username+':'+sim_cred.api_key
					_auth = _auth.encode('ASCII') 
					auth = base64.b64encode(_auth)
				else:
					_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
					_auth = _auth.encode('ASCII') 
					auth = base64.b64encode(_auth)

				status = send_message_tele_module(sim_iccid.iccid, auth, app_conf.key_value, sim_iccid.model)
				return status
			elif sim_iccid.provider == 'pod':
				status = send_message_pod_module(sim_iccid.iccid, app_conf.key_value, sim_iccid.model)
				return status
			elif sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
				status = send_message_pod_multi_module(sim_iccid.iccid, app_conf.key_value, sim_iccid.model)
				return status
		else:
			subject = 'Error during Sending listener message.'
			content = 'iccid :'+iccid+',\n\nModel : '+sim_iccid.model
			send_error_mail(subject, content)











def send_message_pod_multi_module(iccid, message, model):
	token, accountId = get_pod_token()
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/sms"
	headers = {
	    'x-access-token': token,
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache",
	    }

	if message:
		try:
			payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"message\": \""+message+"\",\n  \"dcs\": \"\"\n}"
			response = requests.request("POST", url, data=payload, headers=headers)
			if str(response.status_code) == "200":
				return True
			else:
				subject = 'Error during sending message to pod sim, please look into the server and admin configuration table.'
				content = 'iccid :'+iccid+',\n\nMessage : '+message
				send_error_mail(subject, content)
				return False
		except(Exception)as e:
			subject = 'Error during sending message to pod sim, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nMessage : '+message
			send_error_mail(subject, content)
	else:
		subject = 'Error during sending message to pod sim, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\nMessage : '+message
		send_error_mail(subject, content)
		return False





def send_message_tele_module(iccid, auth, message, model):
	url = "https://restapi3.jasper.com/rws/api/v1/devices/"+iccid+"/smsMessages"
	if message:
		payload = "{\n\t\"messageText\":\""+message+"\"\n}"
		headers = {
		    'Authorization': "Basic "+auth.decode("utf-8"),
		    'Content-Type': "application/json",
		    'Cache-Control': "no-cache"
		    }
		response = requests.request("POST", url, data=payload, headers=headers)
		if str(response.status_code) == "200":
			return True
		else:
			return False

def send_message_pod_module(iccid, message, model):
	token, accountId = get_pod_token()

	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/sms"
	headers = {
	    'x-access-token': token,
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache",
	    }

	if message:
		payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"message\": \""+message+"\",\n  \"dcs\": \"\"\n}"
		response = requests.request("POST", url, data=payload, headers=headers)
		if str(response.status_code) == "200":
			return True
		else:
			subject = 'Error during sending message to pod sim, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nMessage : '+message
			send_error_mail(subject, content)
			return False
	else:
		subject = 'Error during sending message to pod sim, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\nMessage : '+message
		send_error_mail(subject, content)
		return False


def send_pod_multi_message(iccid, plan_id, model, accountId, token):

	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/sms"
	headers = {
	    'x-access-token': token,
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache",
	    }

	message_text = AppConfiguration.objects.filter(key_name=plan_id).first()
	if message_text:
		message = message_text.key_value.replace('model', model)
		payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"message\": \""+message+"\",\n  \"dcs\": \"\"\n}"
		response = requests.request("POST", url, data=payload, headers=headers)
		if str(response.status_code) == "200":
			return True
		else:
			subject = 'Error during sending message to pod sim, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
			send_error_mail(subject, content)
			return False
	else:
		subject = 'No message present in AppConfiguration for model - {}.'.format(model)
		content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
		send_error_mail(subject, content)
		return False



