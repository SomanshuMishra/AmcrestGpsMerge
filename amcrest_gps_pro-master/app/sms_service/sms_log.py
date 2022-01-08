from app.models import *
from django.db import close_old_connections
from app.serializers import *

def save_sms_log(imei, customer_id, message):
	log = {
		'imei':imei,
		'customer_id':customer_id,
		'message' : message
	}
	serializer = SmsLogSerializer(data=log)
	if serializer.is_valid():
		serializer.save()
		close_old_connections()