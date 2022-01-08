from app.models import *
from services.models import *
from services.serializers import *
from services.mail_sender import *
from services.device_listing import *

import requests
import base64
import asyncio



# AT+GTSRI=gl300,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$
# AT+GTSRI=gl300m,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$



def send_pod_multi_model_message(iccid, device_model, auth):
	url = "https://api.podgroup.com/v1/apps/sims/"+iccid+"/sms"
	querystring = {"apikey":auth}
	message_text = AppConfiguration.objects.filter(key_name=plan_id+'_pod_message').first()
	headers = {
	    'Content-Type': "application/json",
    	'Cache-Control': "no-cache"
	    }

	if device_model == 'gl300':
		payload = "{\n  \"iccid\": \" "+iccid+"\",\n  \"message\": \"AT+GTSRI=gl300,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$\"\n}"
		response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
		status_code = response.status_code
	elif device_model == 'gl300m':
		payload = "{\n  \"iccid\": \" "+iccid+"\",\n  \"message\": \"AT+GTSRI=gl300m,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$\"\n}"
		response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
		status_code = response.status_code
	else:
		status_code = 400

	if str(status_code) == "200":
		return True
	else:
		subject = 'Error During sending message to the iccid'
		content = 'Payload Message:'+payload
		send_error_mail(subject, content)
		print('Error during sending message')
		return False



def send_tele_model_message(iccid, device_model, auth):
	url = "https://restapi3.jasper.com/rws/api/v1/devices/"+iccid+"/smsMessages"
	message_text = AppConfiguration.objects.filter(key_name=plan_id+'_message').first()
	if message_text:
		
		headers = {
		    'Authorization': "Basic "+auth.decode("utf-8"),
		    'Content-Type': "application/json",
		    'Cache-Control': "no-cache"
		    }

		if device_model == 'gl300':
			payload = "{\n\t\"messageText\":\"AT+GTSRI=gl300,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$\"\n}"
			response = requests.request("POST", url, data=payload, headers=headers)
			status_code = response.status_code
		elif device_model == 'gl300m':
			payload = "{\n\t\"messageText\":\"AT+GTSRI=gl300m,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$\"\n}"
			response = requests.request("POST", url, data=payload, headers=headers)
			status_code = response.status_code
		else:
			status_code = 400

		if str(status_code) == "200":
			return True
		else:
			print('Error during sending message')
			return False


def send_pod_model_message(iccid, device_model, auth):

	if device_model == 'gl300':
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, pod_sim_device_message_email, [iccid, "AT+GTSRI=gl300,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$"])
	elif device_model == 'gl300m':
		loop = asyncio.new_event_loop()
		loop.run_in_executor(None, pod_sim_device_message_email, [iccid, "AT+GTSRI=gl300m,4,,1,40.121.208.52,13000,192.0.0.0,0,,0,0,0,0,,,FFFF$"])
	pass




