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

# years = [2020]
# months = [1,2,3,4,5,6]
# days = [1, 2, 3, 4, 5,6 ,7,8,9,10,11,12, 13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30, 31]

years = [2020]
months = [1]
days = [1]

class TripDeleteCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def do(self):
        time_threshold = datetime.datetime.now() - datedelta.datedelta(months=6)
        from_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 00:00:00'
        to_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 23:59:59'

        print(from_date, to_date)

        trips = UserTrip.objects.filter(record_date__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')).all()
        print(trips)
        for trip in trips:
            TripsMesurement.objects.filter(measure_id=trip.measure_id).delete()
            trip.delete()

        # TripCalculationGLCron.objects.filter(send_time__gte=20210417235959).delete()
        # try:
        #     trips = UserTrip.objects.filter(record_date__lt=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all()
        #     for trip in trips:
        #         trip_measurment = TripsMesurement.objects.filter(measure_id=trip.measure_id).delete()
        #         if trip:
        #             trip.delete()
        # except(Exception)as e:
        #     print(e)
        
        # for year in years:
        #     for month in months:
        #         for day in days:
        #             print(day)
        #             try:
        #                 date = str(2020)+'-'+str(9)+'-'+str(1)+' 00:00:00'
        #                 to_date = str(2020)+'-'+str(9)+'-'+str(30)+' 23:59:59'
        #             except(Exception)as e:
        #                 print(e)

        #             try:
        #                 # if datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S') > datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S'):  
        #                 if True:                          
        #                     trips = UserTrip.objects.filter(record_date__gte=datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S'), record_date__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')).all()
                            
        #                     for trip in trips:
        #                         print(trip.record_date)
        #                         trip_measurment = TripsMesurement.objects.filter(measure_id=trip.measure_id).delete()
        #                         if trip:
        #                             print('trip deleted')
        #                             # UserTrip.objects.filter(id=trip.id).delete()
        #                             trip.delete()
        #                         print('deleted', date)
        #             except(Exception)as e:
        #                 print(e)

        # user_trip = UserTrip.objects.first()
        # print(user_trip.record_date)
        pass