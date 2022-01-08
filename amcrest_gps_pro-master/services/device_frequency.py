from app.models import *
from services.models import *
from services.serializers import *
from services.mail_sender import *
from services.helper import *
from django.db import close_old_connections

import requests
import base64
import asyncio



# def activate_sim_list(imei_list, plan_id, send_message_flag):
# 	for imei in imei_list:
# 		args = [imei, plan_id, send_message_flag]
# 		loop = asyncio.new_event_loop()
# 		loop.run_in_executor(None, sim_activate_requests, args)

def update_device_frequency(imei, frequency):
	sim_iccid = SimMapping.objects.filter(imei=imei).first()

	if sim_iccid:
		save_command(imei, frequency, sim_iccid.model)
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

			status = send_message(sim_iccid.iccid, frequency, auth, sim_iccid.model)
			print(status, '------------------')
			return status
		elif sim_iccid.provider == 'pod':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='pod_credentials').first()
			status = send_pod_message(sim_iccid.iccid, frequency, sim_cred.api_key, sim_iccid.model)
			return status
		elif sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='pod_credentials').first()
			status = send_pod_multi_message(sim_iccid.iccid, sim_cred.api_key, frequency, sim_iccid.model)
			return status
		
		subject = 'Update Frequency'
		content = 'ICCID :'+sim_iccid.iccid+'\n\nProvider :'+sim_iccid.provider+'\n\nFrequency :'+frequency
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, send_information_mail_async, [subject, content])




def save_command(imei, frequency, model):
	message_text = AppConfiguration.objects.filter(key_name=frequency).first()
	if message_text:

		message = message_text.key_value.replace('model', model)
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
		subject = 'Error during saving command, please look into the app configuration table.'
		content = 'imei :'+imei+',\n\nFrequency : '+frequency
		send_error_mail(subject, content)
		return False


def send_pod_multi_message(iccid, auth, plan_id, model):
	token, accountId = get_pod_token()

	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/sms"
	headers = {
	    'x-access-token': token,
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache",
	    }

	message_text = AppConfiguration.objects.filter(key_name=plan_id).first()
	close_old_connections()
		

	if message_text:
		message = message_text.key_value.replace('model', model)
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

def send_message(iccid, frequency, auth, model):
	url = "https://restapi3.jasper.com/rws/api/v1/devices/"+iccid+"/smsMessages"
	message_text = AppConfiguration.objects.filter(key_name=frequency).first()
	close_old_connections()
	if message_text:
		message = message_text.key_value.replace('model', model)
		payload = "{\n\t\"messageText\":\" "+message+"\"\n}"
		headers = {
		    'Authorization': "Basic "+auth.decode("utf-8"),
		    'Content-Type': "application/json",
		    'Cache-Control': "no-cache"
		    }
		response = requests.request("POST", url, data=payload, headers=headers)
		print(response.text, 'ppppppppppppppppppp')
		if str(response.status_code) == "200":
			return True
		else:
			print('Error during sending message')
			return False
	return False


def send_pod_message(iccid, frequency, auth, model):
	token, accountId = get_pod_token()

	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/sms"
	headers = {
	    'x-access-token': token,
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache",
	    }

	message_text = AppConfiguration.objects.filter(key_name=frequency).first()

	if message_text:
		message = message_text.key_value.replace('model', model)
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




