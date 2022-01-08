from app.models import *
from services.models import *
from services.serializers import *
from services.mail_sender import *

import requests
import base64
import asyncio

def activate_device_listing(iccid):
	subscription = Subscription.objects.filter(imei_iccid=iccid).last()
	if subscription:
		subscription.device_listing = True
		subscription.save()
	pass


def deactivate_device_listing(iccid):
	subscription = Subscription.objects.filter(imei_iccid=iccid).last()
	if subscription:
		subscription.device_listing = False
		subscription.save()
	pass


def save_cron_device_list(iccid, schedule_date):
	serializer = DeviceListingCronSerializer(data={'iccid':iccid, 'date':schedule_date})
	if serializer.is_valid():
		serializer.save()
	else:
		print(serializer.errors)
	pass