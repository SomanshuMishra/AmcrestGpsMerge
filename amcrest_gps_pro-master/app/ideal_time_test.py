from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from app.events.trips import trip_event_module
from app.events.odometer import odometere_event_module
from app.events.fuel_emission import fuel_emission_module

import string
import random
from datetime import datetime, timedelta
import time
import _thread
import pytz
import json

from .serializers import *
from .models import *

from listener.models import *
from listener.serializers import *

from app.location_finder import *

from services.models import *




class GenerateIdealTimeApiView(APIView):
    # permission_classes = (AllowAny,)
    def post(self, request):
        if request.data.get('imei'):
            date_splited = request.data.get('date', None).split('-')
            date, month, year = date_splited[0], date_splited[1], date_splited[2]
            if self.get_category(request.data.get('imei')) == 'obd':
                trip_calculation = CalculateObd24Trip(request.data.get('imei'), date, month, year)
                trip_calculation.calculate()
            elif self.get_category(request.data.get('imei')) == 'gps':
                trip_calculation = CalculateGl24Trip(request.data.get('imei'), date, month, year)
                trip_calculation.calculate()
            else:
                return JsonResponse({'message':'Category Not Defined, cannot generate trip', 'status':False, 'status_code':400}, status=200)
            return JsonResponse({'message':'Ideal Time Generated Successfully', 'status':True, 'status_code':200}, status=200)
        return JsonResponse({'message':'IMEI and Date Required', 'status':False, 'status_code':400}, status=400)


    def get_category(self, imei):
        category = SimMapping.objects.filter(imei=imei).last()
        if category:
            return category.category
        return None


    def check_frequency(self, imei):
        setting = SettingsModel.objects.filter(imei=imei).last()
        if setting:
            if setting.device_frequency_value:
                if setting.device_frequency_value >= 5:
                    return False
                return True
            return True
        return True




User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'

class CalculateGl24Trip:

    def __init__(self, imei, day, month, year):
        self.imei_list = []
        self.trip_id = None

        self.trip_id = None
        self.imei = imei
        self.day = day
        self.month = month
        self.year = year
        self.timestamp_start = None
        self.timestamp_end = None

    def calculate(self):
        import datetime
        timezone = self.get_time_zone(self.imei)
        if timezone:
            self.get_date_to_filter(timezone, self.day, self.month, self.year)
            try:
                get_data = self.get_data()
                # print(list(get_data))
            except(Exception)as e:
                print(e)

            try:
                self.calculate_trip(get_data, self.imei)
            except(Exception)as e:
                print(e)
                pass


    def get_data(self):
        stt = SttMarkers.objects.filter(imei=self.imei, record_date__range=[self.timestamp_start, self.timestamp_end]).all()
        stt_serializer = SttMarkersSerializer(stt, many=True).data
        # print(stt_serializer)
        fri = GLFriMarkers.objects.filter(imei=self.imei, record_date__range=[self.timestamp_start, self.timestamp_end], gps_accuracy__gt=0, report_name="+RESP:GTFRI").all()
        fri_serializer = GLFriMarkersSerializer(fri, many=True).data
        data = list(stt_serializer)+list(fri_serializer)
        records = sorted(data, key = lambda i: i['send_time'],reverse=False)
        return records



    def get_date_to_filter(self, timezone, day, month, year):
        timestamp_start = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', time_fmt)
        timestamp_end = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', time_fmt)
        my_timestamp = datetime.datetime.now() # some timestamp
        old_timezone = pytz.timezone(timezone)
        new_timezone = pytz.timezone("UTC")
        self.timestamp_start = old_timezone.localize(timestamp_start).astimezone(new_timezone)
        self.timestamp_end = old_timezone.localize(timestamp_end).astimezone(new_timezone)

        self.user_start_time = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:01', time_fmt)
        self.user_end_time = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', time_fmt)


    def calculate_trip(self, records, imei):
        import datetime

        GpsIdealTime.objects.filter(imei=imei, record_date_timezone=self.user_end_time.date()).delete()

        last_send_time = ''
        last_mileage = 0
        distance = 0
        time = 0
        last_lat = ''
        last_long = ''
        trip_log = []

        check_for_ideal = False
        ideal_time = 0
        stt_22_record = None

        records = sorted(records, key = lambda i: i['send_time'],reverse=False)
        for record in records:
            if record.get('report_name', None) and record.get('mileage'):
                details = record
                details['send_time'] = str(record['send_time'])
                
                if details.get('gps_accuracy') not in ['0', 0] and details.get('mileage', None) and details.get('latitude', None) != 0 and details.get('longitude', None) != 0:
                    if not trip_log:
                        last_send_time = str(details.get('send_time'))
                        last_mileage = float(details.get('mileage'))
                        trip_log.append(details)
                    else:
                        if last_lat != details.get('latitude') and last_long != details.get('longitude'):
                            mean_time_diff = self.make_time_diff(last_send_time, str(details.get('send_time')))

                            try:
                                average_time_diff = mean_time_diff/60
                            except(Exception) as e:
                                average_time_diff = 0

                            if average_time_diff<5:
                                distance += float(details.get('mileage')) - last_mileage
                                time += mean_time_diff
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))

                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')
                            else:
                                # print(imei, distance, time, trip_log)
                                if check_for_ideal:
                                    if stt_22_record:
                                        print(average_time_diff, 'current send time', details.get('send_time'), 'old send time', stt_22_record.get('send_time'))
                                        

                                        self.save_ideal_time(imei, stt_22_record.get('send_time'), details.get('send_time'), average_time_diff, stt_22_record, details, self.user_start_time)

                                trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                                distance = 0
                                time = 0
                                trip_log = []
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))
                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')

                elif '+RESP:GTSTT' in details.get('report_name', None):
                    if details.get('state', None) == 42 or details.get('state', None) == 22:
                        if not trip_log:
                            check_for_ideal = True
                            stt_22_record = details

                            last_send_time = str(details.get('send_time'))
                            last_mileage = float(details.get('mileage'))
                            trip_log.append(details)
                        else:
                            trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                            trip_log = []
                            distance = 0

                            check_for_ideal = True
                            stt_22_record = details

                            trip_log.append(details)
                            last_send_time = str(details.get('send_time'))
                            last_mileage = float(details.get('mileage'))
                            time = 0
                    elif details.get('state', None) == 41 or details.get('state', None) == 21:
                        if trip_log:
                            distance += float(details.get('mileage')) - last_mileage
                            time += self.make_time_diff(last_send_time, str(details.get('send_time')))
                            trip_log.append(details)
                            trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                            last_send_time = None
                            last_mileage = None
                            distance = 0
                            time = 0
                            trip_log = []
                        else:
                            pass
        # print(imei, distance, time, trip_log)
        trip_c = self.transfer_to_trip(imei, distance, time, trip_log)


    def delete_measurment(self, measure_id):
        trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
        if trips_measure:
            trips_measure.delete()
        pass


    def save_ideal_time(self, imei, prev_send_time, current_send_time, ideal_time, prev_details, current_details, time_timezone):
        try:
            serializer = GpsIdealTimeSerializer(
                data = {
                    "imei" : imei,
                    "ideal_time" : "{:.2f}".format(ideal_time),
                    "from_send_time" : prev_send_time,
                    "to_send_time" : current_send_time,
                    "start_record" : str(json.dumps(prev_details)),
                    "end_record" : str(json.dumps(current_details)),
                    "record_date_timezone" : time_timezone.date()
                }
                )

            if serializer.is_valid():
                serializer.save()
            else:
                pass
        except(Exception)as e:
            pass


    def make_time_diff(self, old_time, new_time):
        try:
            time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
                time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
            # print(time_diff)
        except(Exception)as e:
            # print(e)
            time_diff = 0
        return time_diff


    def get_time_zone(self, imei):
        # print('get_time_zone')
        sub = Subscription.objects.filter(imei_no=imei).last()
        # print('get_time_zone')
        if sub:
            try:
                user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
                if user:
                    return user.time_zone
            except(Exception)as e:
                return None
        return None

    def transfer_to_trip(self, imei, total_distance, total_time, log, start_time=None, end_time=None):

        # import datetime
        # get_time_zone = self.get_time_zone(imei)
        # time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        # from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        # to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

        # # print(imei, total_distance, total_time)
        # if total_distance > 0:
        #     user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=self.user_end_time, record_date_timezone__gte=self.user_start_time).first()
        #     if user_trip:
        #         self.trip_id = user_trip.id

        #         if total_distance>0:
        #             check_last_trip = user_trip.trip_log[-1]
        #             current_log = log[0]
        #             time_diff, time_diff_status = self.check_time_diff(imei, str(check_last_trip[-1].get('send_time')), str(current_log.get('send_time')))
        #             if time_diff_status:
        #                 trip_to_be_update = user_trip.trip_log
        #                 trip_to_be_update = trip_to_be_update[-1]+log
        #                 user_trip.trip_log[-1] = trip_to_be_update
        #                 user_trip.start_time = start_time
        #                 user_trip.end_time = end_time
        #                 user_trip.save()
        #                 close_old_connections()
        #                 self.update_existing_trip_mesurement(user_trip.measure_id, total_distance, total_time, abs(time_diff))
        #             else:
        #                 user_trip.trip_log.append(log)
        #                 user_trip.start_time = start_time
        #                 user_trip.end_time = end_time
        #                 user_trip.save()
        #                 self.update_trip_mesurement(user_trip.measure_id, total_distance, total_time)
        #                 # time.sleep(1)
        #         else:
        #             pass
        #     else:
        #         time_to_save = datetime.datetime.strftime(time_timezone, "%Y-%m-%d %H:%M:%S")
        #         customer_id = self.get_customer_id(imei)
        #         user_trip_obj = {
        #             'imei':imei,
        #             'driver_id':'1',
        #             'trip_log':[log],
        #             'measure_id':10,
        #             'record_date_timezone': self.user_start_time,
        #             'start_time' : start_time,
        #             'end_time' : end_time,
        #             'customer_id':customer_id
        #         }
        #         serializer = UserTripSerializer(data = user_trip_obj)
        #         if serializer.is_valid():
        #             serializer.save()
        #             close_old_connections()
        #             self.update_trip_mesurement(serializer.data['measure_id'], total_distance, total_time)
        #             self.trip_id = serializer.data['id']
        #         else:
        #             print(serializer.errors)
        #             pass
        pass

    def get_customer_id(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        return str(sub.customer_id)

    def check_time_diff(self, imei, old_time, new_time):
        time_diff_seconds = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
            time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))

        # print(time_diff_seconds)
        try:
            time_diff = time_diff_seconds/60
        except(Exception) as e:
            # print(e)
            time_diff = 0

        if time_diff>= 5:#self.get_trip_timeout(imei):
            # print('trip timeout')
            return time_diff_seconds, False
        else:
            # print('trip timeout1')
            return time_diff_seconds, True

    def update_trip_mesurement(self, measure_id, distance, time):
        trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
        if trips_measure:
            trips_measure.total_distance.append(round(distance, 2))
            trips_measure.total_time.append(str(timedelta(seconds=time)))
            trips_measure.save()
            close_old_connections()
        else:
            trip_measure_obj = {
                'total_distance':[round(distance, 2)],
                'total_time':[str(timedelta(seconds=time))],
                'measure_id': measure_id
            }
            serializer = TripsMesurementSerializer(data=trip_measure_obj)
            if serializer.is_valid():
                serializer.save()
                close_old_connections()
            else:
                pass


    def get_trip_timeout(self, imei):
        setting = SettingsModel.objects.filter(imei=imei).last()
        close_old_connections()
        if setting:
            try:
                if setting.trip_end_timer > setting.device_frequency_value:
                    return setting.trip_end_timer
                elif setting.device_frequency_value and setting.device_frequency_value > 0:
                    return float(setting.device_frequency_value)*2
                else:
                    return 10
            except(Exception)as e:
                return 10
        return 10

    def update_existing_trip_mesurement(self, measure_id, distance, time, time_diff):
        import datetime
        trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
        if trips_measure:
            distance_sum = trips_measure.total_distance[-1]

            try:
                time_sum = abs(trips_measure.total_time[-1])
            except(Exception)as e:
                time_sum = trips_measure.total_time[-1]

            try:
                time_diff = abs(time+time_diff)
            except(Exception)as e:
                time_diff = time + time_diff

            try:
                calculated_time = str(timedelta(seconds=time_diff))
            except(Exception)as e:
                calculated_time = str(timedelta(seconds=time_diff))

            time_sum_object = datetime.datetime.strptime(time_sum, "%H:%M:%S")
            calculated_time_object = datetime.datetime.strptime(calculated_time, "%H:%M:%S")

            time_sum_object = datetime.timedelta(hours=time_sum_object.hour, minutes=time_sum_object.minute, seconds=time_sum_object.second)
            calculated_time_object = datetime.timedelta(hours=calculated_time_object.hour, minutes=calculated_time_object.minute, seconds=calculated_time_object.second)
            trips_measure.total_distance[-1] = round(float(distance_sum)+float(distance), 2)
            trips_measure.total_time[-1] = str(time_sum_object+calculated_time_object)
            trips_measure.save()
            close_old_connections()

