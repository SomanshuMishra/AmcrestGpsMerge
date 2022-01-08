from app.models import *
from services.models import *
from services.serializers import *
from services.mail_sender import *
from services.device_listing import *
from services.sim_message_sender import send_message_listener
from services.helper import *

import requests
import base64
import asyncio
import time
import datetime


def pod_suspend(iccid, accountId, token):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/suspend"
	payload = "{\n  \"accountId\": \""+accountId+"\"\n}"
	headers = {
	    'Content-Type': "application/json",
	    'x-access-token': token,
	    'Cache-Control': "no-cache"
	    }
	response = requests.request("PUT", url, data=payload, headers=headers)
	if str(response.status_code) == "200":
		return True
	return False


def pod_unsuspend(iccid, accountId, token):
	url = "https://api.podiotsuite.com/v3/assets/"+iccid+"/unsuspend"
	payload = "{\n  \"accountId\": \""+accountId+"\"\n}"
	headers = {
	    'Content-Type': "application/json",
	    'x-access-token': token,
	    'Cache-Control': "no-cache"
	    }
	response = requests.request("PUT", url, data=payload, headers=headers)
	if str(response.status_code) == "200":
		return True
	return False