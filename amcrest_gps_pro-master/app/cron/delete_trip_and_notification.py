from django_cron import CronJobBase, Schedule
import json
from datetime import timedelta
import datetime
import time
import pytz
import _thread
import datedelta

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

from app.events.trips import trip_event_module

from services.mail_sender import *

User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'


class TripDeleteCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def do(self):
        time_threshold = datetime.datetime.now() - datedelta.datedelta(months=12)
        
        to_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 00:00:00'

        # user_trips = UserTrip.objects.filter(record_date__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')).all()
        # user_trips.delete()
        # print(UserTrip.objects.filter(record_date__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')).count())

        notification = Notifications.objects.filter(record_time__lte=to_date).delete()
        print(notification)