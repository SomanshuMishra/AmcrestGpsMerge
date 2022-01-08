from django_cron import CronJobBase, Schedule
import json
import datetime
from datetime import timedelta
import time
import pytz
import _thread

from django.db.models.signals import post_save as ps
from django.dispatch import receiver
from django.db import close_old_connections
from django.contrib.auth import get_user_model
from django.db.models import Q as qu

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


class RegisteredNotLoggedIn(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def do(self):
    	yest = datetime.datetime.now() - timedelta(days=1)
    	db_yest = datetime.datetime.now() - timedelta(days=2)
    	users = User.objects.filter(date_joined__range=[db_yest, yest], subuser=False).filter(qu(login_count__isnull=True) | qu(login_count__lt=1)).all()
    	for user in users:
    		registered_not_loggedin_mail([user.emailing_address])