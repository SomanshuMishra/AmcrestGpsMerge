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
from django.db.models import Q

from app.models import UserTrip, TripsMesurement, TripCalculationData, Subscription, SettingsModel, TripCalculationGLCron
from app.serializers import UserTripSerializer, TripsMesurementSerializer, TripCalculationDataSerializer, TripCalculationGLCronSerializer, TripCalculationObdCronSerializer

from app.engine_notification.notification_maker import *
from app.trip_notification import trip_notification_maker

from listener.models import *
from listener.serializers import *

from app.events.trips import trip_event_module

from services.mail_sender import *
from services.models import *
from services.serializers import *
#DeviceNotReportingAlert

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
        devices = Subscription.objects.filter(is_active=True, device_in_use=True, device_listing=True, firstBillingDate__lt=db_yest.date()).values('imei_no').distinct()
        for i in devices:
            check_sim_mapping = SimMapping.objects.filter(imei=i.get('imei_no')).last()
            if check_sim_mapping:
                if check_sim_mapping.category == 'gps':
                    if not self.check_gps_device(i.get('imei_no')):
                        self.send_alert_gps(i.get('imei_no'))
                    else:
                        pass
                elif check_sim_mapping.category == 'obd':
                    if not self.check_obd_device(i.get('imei_no')):
                        self.send_alert_obd(i.get('imei_no'))
                    else:
                        pass
                else:
                    pass
            else:
                pass
        pass

    def check_gps_device(self, imei):
    	yest = datetime.datetime.now() - timedelta(days=15)
    	gl_fri = GLFriMarkers.objects.filter(imei=imei, gps_accuracy__gt=0, record_date__gte=yest).exclude(latitude = 0, longitude = 0, speed=0).all()
    	if not gl_fri:
    		return False
    	return True


    def check_obd_device(self, imei):
    	yest = datetime.datetime.now() - timedelta(days=15)
    	obd = ObdMarkers.objects.filter(imei=imei, record_date__gte=yest, gps_accuracy__gt=0).exclude(latitude = 0, longitude = 0, speed=0).all()
    	if not obd:
    		return False
    	return True

    def send_alert_gps(self, imei):
    	if not DeviceNotReportingAlert.objects.filter(imei=imei, record_date__gte=datetime.datetime.now() - timedelta(days=30)).last():
    		mail_id = self.get_user_mail_id(imei)

    		if mail_id:
    			device_not_reporting_mail([mail_id, imei])
    			serializer = DeviceNotReportingAlertSerializer(data={'imei':imei})
    			if serializer.is_valid():
    				serializer.save()


    def send_alert_obd(self, imei):
    	if not DeviceNotReportingAlert.objects.filter(imei=imei, record_date__gte=datetime.datetime.now() - timedelta(days=30)).last():
    		mail_id = self.get_user_mail_id(imei)
    		if mail_id:
    			device_not_reporting_mail([mail_id, imei])
    			serializer = DeviceNotReportingAlertSerializer(data={'imei':imei})
    			if serializer.is_valid():
    				serializer.save()

    def get_user_mail_id(self, imei):
    	sub = Subscription.objects.filter(is_active=True, device_in_use=True, device_listing=True, imei_no=imei).last()
    	if sub:
    		user = User.objects.filter(customer_id=sub.customer_id, subuser=False).last()
    		if user:
    			return user.emailing_address
    		return None
    	return None