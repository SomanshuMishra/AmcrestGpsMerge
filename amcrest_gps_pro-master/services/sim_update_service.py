from app.models import *
from services.models import *
from services.serializers import *
from services.mail_sender import *
from services.device_listing import *
from services.sim_message_sender import send_message_listener
from services.helper import *
from services.pod_sim_status_change import *

import requests
import base64
import asyncio
import time
import datetime



def activate_sim_list(imei_list, plan_id, send_message_flag):
	for imei in imei_list:
		args = [imei, plan_id, send_message_flag]
		try:
			sim_activate_requests(args)
			# loop = asyncio.new_event_loop()
			# loop.run_in_executor(None, sim_activate_requests, args)
		except(Exception)as e:
			print(e)
			subject = 'Error during Applying bundle to pod multi sim, please look into the server and admin configuration table.'
			content = 'IMEI :'+imei+',\n\nPlan : '+plan_id
			send_error_mail(subject, content)

def sim_activate_requests(args):
	imei = args[0]
	plan_id = args[1]
	message_flag = args[2]
	sim_iccid = SimMapping.objects.filter(imei=imei).first()
	if sim_iccid:
		save_command(imei, plan_id, sim_iccid.model)
		if sim_iccid.provider == 'tele2':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
			if sim_cred:
				_auth = sim_cred.username+':'+sim_cred.api_key
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			else:
				_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			activate_sim(sim_iccid.iccid, auth, plan_id, message_flag, sim_iccid.model)
			activate_device_listing(sim_iccid.iccid)
			send_message_listener(imei)
		elif sim_iccid.provider == 'pod':
			# sim_cred = SimUpdateCredentials.objects.filter(key_name='pod_credentials').first()
			status = activate_pod_sim(sim_iccid.iccid, plan_id, sim_iccid.model)
			activate_device_listing(sim_iccid.iccid)
			send_message_listener(imei)
			return status
		elif sim_iccid.provider == 'pod_multi':
			status = activate_pod_multi_sim(sim_iccid.iccid, plan_id, sim_iccid.model)
			activate_device_listing(sim_iccid.iccid)
			send_message_listener(imei)
			print('pod activated')
			return status
		elif sim_iccid.provider == 'pod_att':
			status = activate_pod_att_sim(sim_iccid.iccid, plan_id, sim_iccid.model)
			activate_device_listing(sim_iccid.iccid)
			send_message_listener(imei)
			print('pod activated')
			return status
			

	pass



def save_command(imei, plan_id, model):
	message_text = AppConfiguration.objects.filter(key_name=plan_id).first()
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
		content = 'imei :'+imei+',\n\nFrequency : '+plan_id
		send_error_mail(subject, content)
		return False

def get_pod_sim_info(iccid, token, accountId):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"?accountId="+accountId
	headers = {
	    'Content-Type': "application/json",
	    'x-access-token': token,
	    'Cache-Control': "no-cache"
	    }
	response = requests.request("GET", url, headers=headers)
	if str(response.status_code) == "200":
		response = response.json()

		if response['status'] == 'active':
			return 'active'
		elif response['status'] == 'suspended':
			return 'suspended'
		elif response['status'] == 'inactive':
			return 'inactive'
	else:
		return False


def activate_pod_att_sim(iccid, plan_id, model):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/subscribe"
	token, accountId = get_pod_token()
	card_info = get_pod_sim_info(iccid, token, accountId)
	if card_info == 'inactive':
		try:
			productId = get_pod_att_product_id()
			payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"subscription\": {\n    \"subscriberAccount\": \""+accountId+"\",\n    \"productId\": \""+productId+"\",\n    \"startTime\": \""+str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"\"\n  }\n}"
			headers = {
			    'Content-Type': "application/json",
			    'x-access-token': token,
			    'Cache-Control': "no-cache"
			    }

			response = requests.request("PUT", url, data=payload, headers=headers)
			if str(response.status_code) == "200":
				response = response.json()
				send_pod_multi_message(iccid, plan_id, model, accountId, token)
				sim_iccid = SimMapping.objects.filter(iccid=iccid).first()
				if sim_iccid:
					sim_iccid.subscription_id = response['subscriptions'][0]['id']
					sim_iccid.save()
				return True
			else:
				subject = 'Error during Activating, please look into the server and admin configuration table.'
				content = 'iccid :'+iccid+',\n\nplan :'+plan_id+'\n\nerror: '+str(response.text)
				send_error_mail(subject, content)
				return False
		except(Exception)as e:
			print(e)
			subject = 'Error during Activating, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nplan :'+plan_id+'\n\nerror: '+str(e)
			send_error_mail(subject, content)
			return False
	elif card_info == 'suspended':
		status = pod_unsuspend(iccid, accountId, token)
		if not status:
			subject = 'Error during Unsuspending, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
			send_error_mail(subject, content)
			return False
		else:
			return True
	elif card_info == 'active':
		return True
	else:
		subject = 'Error during Activating, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
		send_error_mail(subject, content)
		return False

def activate_pod_multi_sim(iccid, plan_id, model):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/subscribe"
	token, accountId = get_pod_token()
	card_info = get_pod_sim_info(iccid, token, accountId)
	if card_info == 'inactive':
		try:
			productId = get_pod_multi_product_id()
			payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"subscription\": {\n    \"subscriberAccount\": \""+accountId+"\",\n    \"productId\": \""+productId+"\",\n    \"startTime\": \""+str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"\"\n  }\n}"
			headers = {
			    'Content-Type': "application/json",
			    'x-access-token': token,
			    'Cache-Control': "no-cache"
			    }

			response = requests.request("PUT", url, data=payload, headers=headers)
			if str(response.status_code) == "200":
				response = response.json()
				send_pod_multi_message(iccid, plan_id, model, accountId, token)
				sim_iccid = SimMapping.objects.filter(iccid=iccid).first()
				if sim_iccid:
					sim_iccid.subscription_id = response['subscriptions'][0]['id']
					sim_iccid.save()
				return True
			else:
				subject = 'Error during Activating, please look into the server and admin configuration table.'
				content = 'iccid :'+iccid+',\n\nplan :'+plan_id+'\n\nerror: '+str(response.text)
				send_error_mail(subject, content)
				return False
		except(Exception)as e:
			print(e)
			subject = 'Error during Activating, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nplan :'+plan_id+'\n\nerror: '+str(e)
			send_error_mail(subject, content)
			return False
	elif card_info == 'suspended':
		status = pod_unsuspend(iccid, accountId, token)
		if not status:
			subject = 'Error during Unsuspending, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
			send_error_mail(subject, content)
			return False
		else:
			return True
	elif card_info == 'active':
		return True
	else:
		subject = 'Error during Activating, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
		send_error_mail(subject, content)
		return False





def activate_pod_sim(iccid, plan_id, model):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/subscribe"
	token, accountId = get_pod_token()
	card_info = get_pod_sim_info(iccid, token, accountId)
	
	if card_info == 'inactive':
		try:
			productId = get_pod_product_id()
			payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"subscription\": {\n    \"subscriberAccount\": \""+accountId+"\",\n    \"productId\": \""+productId+"\",\n    \"startTime\": \""+str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"\"\n  }\n}"
			headers = {
			    'Content-Type': "application/json",
			    'x-access-token': token,
			    'Cache-Control': "no-cache"
			    }

			response = requests.request("PUT", url, data=payload, headers=headers)


			if str(response.status_code) == "200":
				response = response.json()
				send_pod_multi_message(iccid, plan_id, model, accountId, token)
				sim_iccid = SimMapping.objects.filter(iccid=iccid).first()
				if sim_iccid:
					sim_iccid.subscription_id = response['subscriptions'][0]['id']
					sim_iccid.save()
				return True
			else:
				subject = 'Error during Activating, please look into the server and admin configuration table.'
				content = 'iccid :'+iccid+',\n\nplan :'+plan_id+'\n\nerror: '+str(response.text)
				send_error_mail(subject, content)
				return False
		except(Exception)as e:
			subject = 'Error during Activating, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nplan :'+plan_id+'\n\nerror: '+str(e)
			send_error_mail(subject, content)
			return False
	elif card_info == 'suspended':
		status = pod_unsuspend(iccid, accountId, token)
		if not status:
			subject = 'Error during Unsuspending, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
			send_error_mail(subject, content)
			return False
		else:
			return True
	elif card_info == 'active':
		return True
	else:
		subject = 'Error during Activating, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
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



def send_message(iccid, plan_id, auth, model):
	url = "https://restapi3.jasper.com/rws/api/v1/devices/"+iccid+"/smsMessages"
	message_text = AppConfiguration.objects.filter(key_name=plan_id).first()
	if message_text:
		message = message_text.key_value.replace('model', model)
		payload = "{\n\t\"messageText\":\" "+message+"\"\n}"
		headers = {
		    'Authorization': "Basic "+auth.decode("utf-8"),
		    'Content-Type': "application/json",
		    'Cache-Control': "no-cache"
		    }
		response = requests.request("POST", url, data=payload, headers=headers)
		if str(response.status_code) == "200":

			return True
		else:
			print('Error during sending message')
			return False


def send_pod_message(iccid, plan_id, model, accountId, token):
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





def activate_sim(iccid, auth, plan_id, message_flag, model):
	url = settings.SIM_ACTIVATION_LINK+iccid
	payload = "{\n\t\"status\":\"ACTIVATED\"\n}"
	headers = {
	    'Content-Type': "application/json",
	    'Authorization': "Basic "+auth.decode("utf-8"),
	    'Accept': "application/json",
	    'Cache-Control': "no-cache"
	    }
	response = requests.request("PUT", url, data=payload, headers=headers)
	if str(response.status_code) == "200":
		if message_flag:
			print('sending flag')
			send_message(iccid, plan_id, auth, model)
		pass
	else:
		subject = 'Error during Activating sim, please look into the server and admin configuration table or Tele2 website.'
		content = 'iccid :'+iccid+',\n\nPlan : '+plan_id
		send_error_mail(subject, content)
		pass





def apply_bundle(iccid, auth, promotion_name, customer_group=None):
	sim_iccid = SimMapping.objects.filter(iccid=iccid).first()
	if sim_iccid:
		url = "https://api.podgroup.com/v1/apps/sims/"+iccid+"/promotion"
		querystring = {"apikey":auth}

		if customer_group:
			payload = "promotion="+promotion_name+"&customerGroup="+customer_group
		else:
			payload = "promotion="+promotion_name
		headers = {
		    'Content-Type': "application/x-www-form-urlencoded",
		    'Cache-Control': "no-cache"
		    }
		response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
		if str(response.status_code) == "200":
			return True
		else:
			return False



def deactivate_sim(iccid, auth, schedule_date):
	url = settings.SIM_ACTIVATION_LINK+iccid
	payload = "{\n\t\"status\":\"DEACTIVATED\",\n    \"effectiveDate\":\""+schedule_date+"\"\n}"
	headers = {
	    'Content-Type': "application/json",
	    'Authorization': "Basic "+auth.decode("utf-8"),
	    'Accept': "application/json",
	    'Cache-Control': "no-cache"
	    }
	response = requests.request("PUT", url, data=payload, headers=headers)
	if str(response.status_code) == "202":
		print('Deactivated SIM')
		pass
	else:
		print('Error during sim deactivation Sim')
		pass
		

def sim_deactivate_request(args):
	imei = args[0]
	schedule_date = args[1]
	
	sim_iccid = SimMapping.objects.filter(iccid=imei).first()
	
	if sim_iccid:
		if sim_iccid.provider == 'tele2':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
			if sim_cred:
				_auth = sim_cred.username+':'+sim_cred.api_key
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			else:
				_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			deactivate_sim(sim_iccid.iccid, auth, schedule_date)
			save_cron_device_list(sim_iccid.iccid, schedule_date[:-1])
		elif sim_iccid.provider == 'pod' or sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
			serialzer = PodSimCronSerializer(data={'iccid':sim_iccid.iccid, "date":schedule_date[:-1]})
			if serialzer.is_valid():
				serialzer.save()
			else:
				print(serialzer.errors)
	pass




def sim_deactivate_immeidiate_request(imei):
	sim_iccid = SimMapping.objects.filter(imei=imei).last()
	if sim_iccid:
		if sim_iccid.provider == 'tele2':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
			if sim_cred:
				_auth = sim_cred.username+':'+sim_cred.api_key
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			else:
				_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			status = deactivate_sim_immeidiate(sim_iccid.iccid, auth)
			deactivate_device_listing(sim_iccid.iccid)
			return status
		elif sim_iccid.provider == 'pod' or sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
			# sim_cred = SimUpdateCredentials.objects.filter(key_name='pod_credentials').first()
			status = deativate_pod_sim_immeidiate(sim_iccid.iccid)
			deactivate_device_listing(sim_iccid.iccid)
			return status

	return False

def deativate_pod_sim_immeidiate(iccid):
	try:
		token, accountId = get_pod_token()

		url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/suspend"
		payload = "{\n  \"accountId\": \""+accountId+"\"\n}"
		headers = {
		    'Content-Type': "application/json",
		    'x-access-token': token,
		    'Cache-Control': "no-cache"
		    }
		response = requests.request("PUT", url, data=payload, headers=headers)
		print(response.text)
		if str(response.status_code) == "200":
			return True
		else:
			subject = 'Error during Deactivating POD sim.'
			content = 'iccid :'+iccid
			send_error_mail(subject, content)
			return False
	except(Exception)as e:
		print(e, 'pppppppppppp')
		subject = 'Error during Deactivating POD sim.'
		content = 'iccid :'+iccid
		send_error_mail(subject, content)

def deactivate_sim_immeidiate(iccid, auth):
	url = settings.SIM_ACTIVATION_LINK+iccid
	payload = "{\n\t\"status\":\"DEACTIVATED\"\n}"
	headers = {
	    'Content-Type': "application/json",
	    'Authorization': "Basic "+auth.decode("utf-8"),
	    'Accept': "application/json",
	    'Cache-Control': "no-cache"
	    }
	response = requests.request("PUT", url, data=payload, headers=headers)
	if str(response.status_code) == "200":
		return True
	else:
		subject = 'Error during Deactivating POD sim.'
		content = 'iccid :'+iccid
		send_error_mail(subject, content)
		return False

def sim_activate_immeidiate_request(imei):
	sim_iccid = SimMapping.objects.filter(imei=imei).first()
	if sim_iccid:
		if sim_iccid.provider == 'tele2':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
			if sim_cred:
				_auth = sim_cred.username+':'+sim_cred.api_key
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			else:
				_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			status = activate_sim_immeidiate(sim_iccid.iccid, auth)
			activate_device_listing(sim_iccid.iccid)
			return status
		elif sim_iccid.provider == 'pod':
			plan_details = Subscription.objects.filter(imei_no=imei, device_in_use=True).last()
			if plan_details:
				status = activate_pod_sim_immeidiate(sim_iccid.iccid)
				activate_device_listing(sim_iccid.iccid)
				return status
			return False
		elif sim_iccid.provider == 'pod_multi':
			plan_details = Subscription.objects.filter(imei_no=imei, device_in_use=True).last()
			if plan_details:
				status = activate_pod_multi_sim_immeidiate(sim_iccid.iccid, plan_details.activated_plan_id, sim_iccid.model)
				activate_device_listing(sim_iccid.iccid)
				return status
			return False
		elif sim_iccid.provider == 'pod_att':
			plan_details = Subscription.objects.filter(imei_no=imei, device_in_use=True).last()
			if plan_details:
				status = activate_pod_att_sim_immeidiate(sim_iccid.iccid, plan_details.activated_plan_id, sim_iccid.model)
				activate_device_listing(sim_iccid.iccid)
				return status
			return False
	return False



def activate_pod_att_sim_immeidiate(iccid, plan_id, model):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/subscribe"
	token, accountId = get_pod_token()
	card_info = get_pod_sim_info(iccid, token, accountId)
	
	if card_info == 'inactive':
		productId = get_pod_att_product_id()
		payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"subscription\": {\n    \"subscriberAccount\": \""+accountId+"\",\n    \"productId\": \""+productId+"\",\n    \"startTime\": \""+str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"\"\n  }\n}"
		headers = {
		    'Content-Type': "application/json",
		    'x-access-token': token,
		    'Cache-Control': "no-cache"
		    }

		response = requests.request("PUT", url, data=payload, headers=headers)


		if str(response.status_code) == "200":
			response = response.json()
			send_pod_multi_message(iccid, plan_id, model, accountId, token)
			sim_iccid = SimMapping.objects.filter(iccid=iccid).first()
			if sim_iccid:
				sim_iccid.subscription_id = response['subscriptions'][0]['id']
				sim_iccid.save()
			return True
		else:
			subject = 'Error during activating POD sim.'
			content = 'iccid :'+iccid
			send_error_mail(subject, content)
			return False
	elif card_info == 'suspended':
		status = pod_unsuspend(iccid, accountId, token)
		if not status:
			subject = 'Error during Unsuspending, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\n'
			send_error_mail(subject, content)
			return False
		else:
			return True
	elif card_info == 'active':
		return True
	else:
		subject = 'Error during Activating, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\n'
		send_error_mail(subject, content)
		return False



def activate_pod_multi_sim_immeidiate(iccid, plan_id, model):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/subscribe"
	token, accountId = get_pod_token()
	card_info = get_pod_sim_info(iccid, token, accountId)
	
	if card_info == 'inactive':
		productId = get_pod_multi_product_id()
		payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"subscription\": {\n    \"subscriberAccount\": \""+accountId+"\",\n    \"productId\": \""+productId+"\",\n    \"startTime\": \""+str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"\"\n  }\n}"
		headers = {
		    'Content-Type': "application/json",
		    'x-access-token': token,
		    'Cache-Control': "no-cache"
		    }

		response = requests.request("PUT", url, data=payload, headers=headers)


		if str(response.status_code) == "200":
			response = response.json()
			send_pod_multi_message(iccid, plan_id, model, accountId, token)
			sim_iccid = SimMapping.objects.filter(iccid=iccid).first()
			if sim_iccid:
				sim_iccid.subscription_id = response['subscriptions'][0]['id']
				sim_iccid.save()
			return True
		else:
			subject = 'Error during activating POD sim.'
			content = 'iccid :'+iccid
			send_error_mail(subject, content)
			return False
	elif card_info == 'suspended':
		status = pod_unsuspend(iccid, accountId, token)
		if not status:
			subject = 'Error during Unsuspending, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\n'
			send_error_mail(subject, content)
			return False
		else:
			return True
	elif card_info == 'active':
		return True
	else:
		subject = 'Error during Activating, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\n'
		send_error_mail(subject, content)
		return False


def activate_pod_sim_immeidiate(iccid):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/subscribe"
	token, accountId = get_pod_token()
	card_info = get_pod_sim_info(iccid, token, accountId)
	
	if card_info == 'inactive':
		# productId = get_pod_product_id(token, accountId, iccid)
		productId = get_pod_product_id()
		payload = "{\n  \"accountId\": \""+accountId+"\",\n  \"subscription\": {\n    \"subscriberAccount\": \""+accountId+"\",\n    \"productId\": \""+productId+"\",\n    \"startTime\": \""+str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"\"\n  }\n}"
		headers = {
		    'Content-Type': "application/json",
		    'x-access-token': token,
		    'Cache-Control': "no-cache"
		    }

		response = requests.request("PUT", url, data=payload, headers=headers)

		if str(response.status_code) == "200":
			response = response.json()
			send_pod_multi_message(iccid, plan_id, model, accountId, token)
			sim_iccid = SimMapping.objects.filter(iccid=iccid).first()
			if sim_iccid:
				sim_iccid.subscription_id = response['subscriptions'][0]['id']
				sim_iccid.save()
			return True
		else:
			subject = 'Error during Unsuspending, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\nerror : '+response.text
			send_error_mail(subject, content)
			return False
	elif card_info == 'suspended':
		status = pod_unsuspend(iccid, accountId, token)
		if not status:
			subject = 'Error during Unsuspending, please look into the server and admin configuration table.'
			content = 'iccid :'+iccid+',\n\n'
			send_error_mail(subject, content)
			return False
		else:
			return True
	elif card_info == 'active':
		return True
	else:
		subject = 'Error during Activating, please look into the server and admin configuration table.'
		content = 'iccid :'+iccid+',\n\n'
		send_error_mail(subject, content)
		return False

def activate_sim_immeidiate(iccid, auth):
	url = settings.SIM_ACTIVATION_LINK+iccid
	payload = "{\n\t\"status\":\"ACTIVATED\"\n}"
	headers = {
	    'Content-Type': "application/json",
	    'Authorization': "Basic "+auth.decode("utf-8"),
	    'Accept': "application/json",
	    'Cache-Control': "no-cache"
	    }
	response = requests.request("PUT", url, data=payload, headers=headers)
	if str(response.status_code) == "200":

		return True
	else:
		subject = 'Error during activating Tele2 sim.'
		content = 'iccid :'+iccid+'\n Error : '+response.text
		send_error_mail(subject, content)
		return False

def get_sim_status(imei):
	sim_iccid = SimMapping.objects.filter(imei=imei).first()
	if sim_iccid:
		if sim_iccid.provider == 'tele2':
			sim_cred = SimUpdateCredentials.objects.filter(key_name='tele2_credentials').first()
			if sim_cred:
				_auth = sim_cred.username+':'+sim_cred.api_key
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)
			else:
				_auth = settings.SIM_USERNAME+':'+settings.SIM_API_KEY
				_auth = _auth.encode('ASCII') 
				auth = base64.b64encode(_auth)

			url = 'https://restapi3.jasper.com/rws/api/v1/devices/'+sim_iccid.iccid
			headers = {
			    'Content-Type': "application/json",
			    'Authorization': "Basic "+auth.decode("utf-8"),
			    'Accept': "application/json",
			    'Cache-Control': "no-cache"
			    }
			response = requests.request("GET", url, headers=headers)
			if response.ok:
				res = response.json()
				return res.get('status')
			return 'INVALID IMEI'
		elif sim_iccid.provider == 'pod' or sim_iccid.provider == 'pod_multi' or sim_iccid.provider == 'pod_att':
			url = "https://api.podiotsuite.com/v3/assets/"+sim_iccid.iccid+"/subscribe"
			token, accountId = get_pod_token()
			card_info = get_pod_sim_info(sim_iccid.iccid, token, accountId)
			return card_info