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

from app.models import UserTrip, TripsMesurement, TripCalculationData, Subscription, SettingsModel, TripCalculationGLCron, FeaturedUserTrip
from app.serializers import FeaturedUserTripSerializer, UserTripSerializer, TripsMesurementSerializer, TripCalculationDataSerializer, TripCalculationGLCronSerializer, TripCalculationObdCronSerializer

from services.mail_sender import *

User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'


class CloneDataCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def get_imei_list(self):
        self.imei_list = TripCalculationObdCron.objects.distinct(field="imei")

    def do(self):
        import datetime
        self.limits = [[0,1000],[1001,2000], [2001, 3000], [3001, 4000], [4001, 5000], [5001, 6000], [6001, 7000], [7001, 8000], [8001, 9000], [9001, 10000],
        				[10001,11000],[11001,12000], [12001, 13000], [13001, 14000], [14001, 15000], [15001, 16000], [16001, 17000], [17001, 18000], [18001, 19000], [19001, 20000],
        				[20001,21000],[21001,22000], [22001, 23000], [23001, 24000], [24001, 25000], [25001, 26000], [26001, 27000], [27001, 28000], [28001, 29000], [29001, 30000],
        				[30001,31000],[31001,32000], [32001, 33000], [33001, 34000], [34001, 35000], [35001, 36000], [36001, 37000], [37001, 38000], [38001, 39000], [39001, 40000], [40001, 41000]]

        for i in self.limits:
        	user_trips = UserTrip.objects[i[0]:i[1]]
        	try:
        		featured_trip(i[0], i[1])
        		for j in user_trips:
        			fe_trip = FeaturedUserTrip(
        					measure_id = j.measure_id,
							trip_log = j.trip_log,
							imei = j.imei,
							record_date = j.record_date,
							record_date_timezone = j.record_date_timezone,
							driver_id = j.driver_id,
							customer_id = j.customer_id,
							start_time = j.start_time,
							end_time = j.end_time
        				)
        			fe_trip.save()
        			time.sleep(0.5)
        		featured_trip(i[0], i[1])
        	except(Exception)as e:
        		print(e)
        	pass

    def send_cron_mail_now(self, i):
        # featured_trip(i[0], 1[1])
        pass