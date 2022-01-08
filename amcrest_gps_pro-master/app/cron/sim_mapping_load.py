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
import xlrd

User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'

UTC=pytz.UTC

class LoadImeiMachine(CronJobBase):
	RUN_EVERY_MINS = 0
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'app.cron.review_cron'

	def do(self):
		imeis = []

		loc = "app/cron/imei_list/ULYG191024001  20191126   GL300MA  2000PCS (1).XLS"

		try:
			wb = xlrd.open_workbook(loc)
			sheet = wb.sheet_by_index(0)
		except(Exception)as e:
			print('Error During Opening File')

		for i in range(sheet.nrows):
			try:
				if i>=2:
					check_sim = SimMapping.objects.filter(imei=sheet.cell_value(i, 2)).last()
					if not check_sim:
						sim_mapping_dict = {
							"imei":sheet.cell_value(i, 2),
							"iccid":sheet.cell_value(i, 3)[:-1],
							"model":'gl300m',
							"category":'gps',
							"provider":'pod_multi'
						}
						serializer = SimMappingSerializer(data=sim_mapping_dict)
						if serializer.is_valid():
							serializer.save()
						else:
							print(serializer.errors)
							imeis.append(sheet.cell_value(i, 2))
			except(Exception)as e:
				print(e)
				imeis.append(sheet.cell_value(i, 2))

		print(imeis)