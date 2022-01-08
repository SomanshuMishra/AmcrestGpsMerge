from app.models import Notifications, Subscription
from app.serializers import NotificationsSerializer
from django.contrib.auth import get_user_model

import datetime
import pytz

from django.db import close_old_connections


User = get_user_model()
default_time_zone = "UTC"


def save_notifications(imei, title, body, customer_id, report_obj, event_type=None, longitude=None, latitude=None):
	user = User.objects.filter(customer_id=customer_id, subuser=False).first()
	if user:
		if user.time_zone:
			timezone = user.time_zone
		else:
			timezone = default_time_zone

		time_timezone = datetime.datetime.now(pytz.timezone(timezone))
		time_to_save = datetime.datetime.strftime(time_timezone, "%Y-%m-%d %H:%M:%S")

		notification_obj = {
			'customer_id':customer_id,
			'title':title,
			'body':body,
			'imei':imei,
			'record_date_timezone':time_to_save,
			'type':event_type,
			'longitude': longitude, 
			'latitude' : latitude,

			'alert_name':report_obj.get('alert_name'),
			'event':report_obj.get('event'),
			'battery_percentage':report_obj.get('battery_percentage'),
			'location':report_obj.get('location'),
			'speed':report_obj.get('speed')
			}
		serializer = NotificationsSerializer(data=notification_obj)
		if serializer.is_valid():
			serializer.save()
			print('saved00000000000000')
		else:
			print(serializer.errors)
			pass
	close_old_connections()
	pass