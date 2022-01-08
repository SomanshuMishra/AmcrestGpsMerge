from django_cron import CronJobBase, Schedule
import json
from datetime import datetime, timedelta
import time
import pytz
import _thread

from django.db.models.signals import post_save as ps
from django.dispatch import receiver
from django.db import close_old_connections
from django.contrib.auth import get_user_model
from django.db.models import Q

from app.models import UserTrip, TripsMesurement, TripCalculationData, Subscription, SettingsModel, TripCalculationGLCron
from app.serializers import UserTripSerializer, TripsMesurementSerializer, TripCalculationDataSerializer, TripCalculationGLCronSerializer, TripCalculationObdCronSerializer

from app.engine_notification.notification_maker import *
from app.trip_notification import trip_notification_maker

from listener.models import *
from listener.serializers import *

from services.models import *
from services.serializers import *

from app.events.trips import trip_event_module

from services.mail_sender import *

User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'

UTC=pytz.UTC

class DataEntryMachine(CronJobBase):
	RUN_EVERY_MINS = 0
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'app.cron.review_cron'

	def do(self):
		last_month = datetime.datetime.now() - timedelta(minutes=5)
		if self.check_fri_markers(last_month) or self.check_stt_markers(last_month):
			pass
		else:
			try:
				subject = 'Device Not Reported in last 5 min'
				message = 'Device Not Reported in last 5 min '+str(last_month.date())
				send_device_reporting_mail(subject, message)
			except(Exception)as e:
				print(e)

	def check_fri_markers(self, date):
		if GLFriMarkers.objects.filter(record_date__gte=date).all():
			return True
		else:
			return False


	def check_stt_markers(self, date):
		if SttMarkers.objects.filter(record_date__gte=date).all():
			return True
		else:
			return False