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


class TripBackupCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def do(self):
        time_threshold = datetime.datetime.now() - datedelta.datedelta(months=6)
        # time_threshold = datetime.datetime.now() - datedelta.datedelta(days=35)
        print(time_threshold)
        from_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 00:00:00'
        to_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 23:59:59'
        trip_obj = UserTripBackup.objects.filter(record_date__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all()
        
    	
        if not trip_obj:
            user_trips = UserTrip.objects.filter(record_date__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all()
            for user_trip in user_trips:
                serializer = UserTripForBackupSerializer(user_trip)
                trip = serializer.data
                trip['record_date_timezone'] = trip.get('record_date_timezone').replace('T', ' ').replace('Z', '')
                trip['record_date'] = trip.get('record_date').replace('T', ' ').replace('Z', '')

                try:
                    trip_measurment = TripsMesurement.objects.filter(measure_id=trip.get('measure_id')).first()
                    mes_serializer = TripsMesurementSerializer(trip_measurment)
                except(Exception)as e:
                    print(e)

                try:
                    del trip['id']
                    cre_trip = UserTripBackupSerializer(data=trip)
                    if cre_trip.is_valid():
                        cre_trip.save()
                    else:
                        print(cre_trip.errors)

                    trip_measurment_p = mes_serializer.data
                    del trip_measurment_p['id']
                    cre_trip_mes = TripsMesurementBackupSerializer(data=trip_measurment_p)
                    if cre_trip_mes.is_valid():
                        cre_trip_mes.save()
                    else:
                        print(cre_trip_mes.errors)

                    user_trip.delete()
                    trip_measurment.delete()
                except(Exception)as e:
                    print(e)
        else:
            print('trip exists')

        subject = 'Trip Backup Cron Ended'
        message = 'Trip Backup Cron Ended'
        try:
            data_backup_cron_mail_sender(subject, message)
        except(Exception)as e:
            print(e, '---------')
        pass