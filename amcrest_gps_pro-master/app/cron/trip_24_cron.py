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

from app.events.trips import trip_event_module

from services.mail_sender import *

User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'



class CalculateGl24Trip(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def do(self):
        import datetime
        self.get_imei_list()
        for i in self.imei_list:
            if self.check_frequency(i):
                timezone = self.get_time_zone(i)
                if timezone:
                    local_datetime = datetime.datetime.now(pytz.timezone(timezone))
                    date_to_flter = self.get_date_to_filter(timezone, local_datetime.day, local_datetime.month, local_datetime.year)
                    # date_to_flter = self.get_date_to_filter(timezone, 1, local_datetime.month, local_datetime.year)
                    get_data = self.get_data(i, date_to_flter)
                    
                    try:
                        self.calculate_trip(get_data, i)
                    except(Exception)as e:
                        print(e)
                        pass

                    try:
                        delete_record = TripCalculationGLCron.objects.filter(imei=i).all()
                        delete_record.delete()
                    except(Exception)as e:
                        prine(e)
                        pass

                    # time.sleep(1)

                    # try:
                    #     if self.trip_id:
                    #         import asyncio
                    #         loop = asyncio.new_event_loop()
                    #         loop.run_in_executor(None, trip_event_module, [self.trip_id])
                    # except(Exception)as e:
                    #     print(e)

    def check_frequency(self, imei):
        setting = SettingsModel.objects.filter(imei=imei).last()
        if setting:
            if setting.device_frequency_value:
                if setting.device_frequency_value >= 5:
                    return False
                return True
            return True
        return True

    def send_cron_mail_now(self):
        list_ = ",".join(self.imei_list)
        send_cron_mail_24(list_)
        pass


    def get_imei_list(self):
        self.imei_list = TripCalculationGLCron.objects.distinct(field="imei")

    def get_data(self, imei, time_date):

        # stt = SttMarkers.objects.filter(imei=imei, record_date__gte=time_date).exclude(latitude = 0, longitude = 0).all()
        try:
            send_time = int(time_date.strftime("%Y%m%d%H%M%S"))
            stt = SttMarkers.objects.filter(imei=imei, send_time__gte=send_time).exclude(latitude = 0, longitude = 0).all()
        except(Exception)as e:
            stt = SttMarkers.objects.filter(imei=imei, record_date__gte=time_date).exclude(latitude = 0, longitude = 0).all()

        stt_serializer = SttMarkersSerializer(stt, many=True).data

        try:
            send_time = int(time_date.strftime("%Y%m%d%H%M%S"))
            fri = GLFriMarkers.objects.filter(imei=imei, send_time__gte=send_time, gps_accuracy__gt=0).exclude(latitude = 0, longitude = 0, speed=0).all()
        except(Exception)as e:
            fri = GLFriMarkers.objects.filter(imei=imei, record_date__gte=time_date, gps_accuracy__gt=0).exclude(latitude = 0, longitude = 0, speed=0).all()

        
        fri_serializer = GLFriMarkersSerializer(fri, many=True).data
        data = list(stt_serializer)+list(fri_serializer)
        data = [dict(i) for i in data]
        records = sorted(data, key = lambda i: i['send_time'],reverse=False)
        return records



    def get_date_to_filter(self, timezone, day, month, year):
        timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', time_fmt)
        my_timestamp = datetime.datetime.now() # some timestamp
        old_timezone = pytz.timezone(timezone)
        new_timezone = pytz.timezone("UTC")
        my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
        return my_timestamp_in_new_timezone


    def calculate_trip(self, records, imei):
        import datetime
        get_time_zone = self.get_time_zone(imei)
        time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

        user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).first()
        if user_trip:
            user_trip.delete()
            self.delete_measurment(user_trip.measure_id)

        last_send_time = ''
        last_mileage = 0
        distance = 0
        time = 0
        last_lat = ''
        last_long = ''
        trip_log = []

        records = sorted(records, key = lambda i: i['send_time'],reverse=False)

        for record in records:
            if record.get('report_name', None):
                details = record
                details['send_time'] = str(record['send_time'])
                if details.get('gps_accuracy') not in ['0', 0] and details.get('mileage', None) and details.get('latitude', None) != 0 and details.get('longitude', None) != 0 and float(details.get('mileage'))>=last_mileage: #and float(details.get('mileage'))>last_mileage
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

                            if average_time_diff > 6:
                                # print(imei, distance, time, trip_log)
                                trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                                # time.sleep(1)
                                distance = 0
                                time = 0
                                trip_log = []
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))
                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')
                            else:
                                distance += float(details.get('mileage')) - last_mileage
                                time += mean_time_diff
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))
                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')
                        else:
                            print('not matching')
                            pass
                                

                elif ('+RESP:GTSTT' in details.get('report_name', None) or '+BUFF:GTSTT' in details.get('report_name', None)) and details.get('latitude', None) != 0 and details.get('longitude', None) != 0 and float(details.get('mileage'))>=last_mileage:
                    if details.get('state', None) == 42 or details.get('state', None) == 22:
                        if not trip_log:
                            last_send_time = str(details.get('send_time'))
                            last_mileage = float(details.get('mileage'))
                            trip_log.append(details)
                        else:
                            trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                            # time.sleep(1)
                            trip_log = []
                            distance = 0
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
                            # time.sleep(1)
                            last_send_time = None
                            last_mileage = 0
                            distance = 0
                            time = 0
                            trip_log = []
                        else:
                            pass
        # print(imei, distance, time, trip_log)
        trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
        # time.sleep(1)


    def delete_measurment(self, measure_id):
        trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
        if trips_measure:
            trips_measure.delete()
        pass


    def make_time_diff(self, old_time, new_time):
        try:
            time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
                time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
        except(Exception)as e:
            print(e)
            time_diff = 0
        return time_diff


    def get_time_zone(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        if sub:
            try:
                user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
                if user:
                    return user.time_zone
            except(Exception)as e:
                print(e)
                return None
        return None

    def transfer_to_trip(self, imei, total_distance, total_time, log, start_time=None, end_time=None):
        import datetime
        get_time_zone = self.get_time_zone(imei)
        time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

        # print(imei, total_distance, total_time, log)
        if total_distance >= 0.1:
            user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).first()
            if user_trip:
                self.trip_id = user_trip.id

                if total_distance>0:
                    check_last_trip = user_trip.trip_log[-1]
                    current_log = log[0]
                    time_diff, time_diff_status = self.check_time_diff(imei, str(check_last_trip[-1].get('send_time')), str(current_log.get('send_time')))
                    if time_diff_status:
                        trip_to_be_update = user_trip.trip_log
                        trip_to_be_update = trip_to_be_update[-1]+log
                        user_trip.trip_log[-1] = trip_to_be_update
                        user_trip.start_time = start_time
                        user_trip.end_time = end_time
                        user_trip.save()
                        close_old_connections()
                        self.update_existing_trip_mesurement(user_trip.measure_id, total_distance, total_time, abs(time_diff))
                    else:
                        user_trip.trip_log.append(log)
                        user_trip.start_time = start_time
                        user_trip.end_time = end_time
                        user_trip.save()
                        self.update_trip_mesurement(user_trip.measure_id, total_distance, total_time)
                        # time.sleep(1)
                else:
                    pass
            else:
                time_to_save = datetime.datetime.strftime(time_timezone, "%Y-%m-%d %H:%M:%S")
                customer_id = self.get_customer_id(imei)
                user_trip_obj = {
                    'imei':imei,
                    'driver_id':'1',
                    'trip_log':[log],
                    'measure_id':10,
                    'record_date_timezone': time_to_save,
                    'start_time' : start_time,
                    'end_time' : end_time,
                    'customer_id':customer_id
                }
                # print(user_trip_obj['time_to_save'])
                serializer = UserTripSerializer(data = user_trip_obj)

                if serializer.is_valid():
                    serializer.save()
                    close_old_connections()
                    self.update_trip_mesurement(serializer.data['measure_id'], total_distance, total_time)
                    self.trip_id = serializer.data['id']
                else:
                    print(serializer.errors)
                    pass


    def get_customer_id(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        return str(sub.customer_id)

    def check_time_diff(self, imei, old_time, new_time):
        time_diff_seconds = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
            time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))

        try:
            time_diff = time_diff_seconds/60
        except(Exception) as e:
            time_diff = 0

        if time_diff>= self.get_trip_timeout(imei):
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
                    return float(setting.trip_end_timer)
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



class CalculateGl24TripHighFrequency(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def do(self):
        import datetime
        self.get_imei_list()
        # self.imei_list = ['015181002850247']
        for i in self.imei_list:
            # print(i)
            if self.check_frequency(i):
                timezone = self.get_time_zone(i)
                if timezone:
                    local_datetime = datetime.datetime.now(pytz.timezone(timezone))
                    date_to_flter = self.get_date_to_filter(timezone, local_datetime.day, local_datetime.month, local_datetime.year)
                    get_data = self.get_data(i, date_to_flter)
                    
                    try:
                        self.calculate_trip(get_data, i)
                    except(Exception)as e:
                        print(e)
                        pass

                    try:
                        delete_record = TripCalculationGLCron.objects.filter(imei=i).all()
                        delete_record.delete()
                    except(Exception)as e:
                        prine(e)
                        pass

                    # time.sleep(1)

                    # try:
                    #     if self.trip_id:
                    #         import asyncio
                    #         loop = asyncio.new_event_loop()
                    #         loop.run_in_executor(None, trip_event_module, [self.trip_id])
                    # except(Exception)as e:
                    #     print(e)

    def check_frequency(self, imei):
        setting = SettingsModel.objects.filter(imei=imei).last()
        if setting:
            if setting.device_frequency_value:
                if setting.device_frequency_value >= 5 and setting.device_frequency_value <= 15:
                    return True
                return False
            return False
        return False

    def send_cron_mail_now(self):
        list_ = ",".join(self.imei_list)
        send_cron_mail_24(list_)
        pass


    def get_imei_list(self):
        self.imei_list = TripCalculationGLCron.objects.distinct(field="imei")

    def get_data(self, imei, time_date):

        # stt = SttMarkers.objects.filter(imei=imei, record_date__gte=time_date).exclude(latitude = 0, longitude = 0).all()
        try:
            send_time = int(time_date.strftime("%Y%m%d%H%M%S"))
            stt = SttMarkers.objects.filter(imei=imei, send_time__gte=send_time).exclude(latitude = 0, longitude = 0).all()
        except(Exception)as e:
            stt = SttMarkers.objects.filter(imei=imei, record_date__gte=time_date).exclude(latitude = 0, longitude = 0).all()

        stt_serializer = SttMarkersSerializer(stt, many=True).data

        try:
            send_time = int(time_date.strftime("%Y%m%d%H%M%S"))
            fri = GLFriMarkers.objects.filter(imei=imei, send_time__gte=send_time, gps_accuracy__gt=0).exclude(latitude = 0, longitude = 0, speed=0).all()
        except(Exception)as e:
            fri = GLFriMarkers.objects.filter(imei=imei, record_date__gte=time_date, gps_accuracy__gt=0).exclude(latitude = 0, longitude = 0, speed=0).all()

        
        fri_serializer = GLFriMarkersSerializer(fri, many=True).data
        data = list(stt_serializer)+list(fri_serializer)
        data = [dict(i) for i in data]
        records = sorted(data, key = lambda i: i['send_time'],reverse=False)
        return records



    def get_date_to_filter(self, timezone, day, month, year):
        timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', time_fmt)
        my_timestamp = datetime.datetime.now() # some timestamp
        old_timezone = pytz.timezone(timezone)
        new_timezone = pytz.timezone("UTC")
        my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
        return my_timestamp_in_new_timezone


    def calculate_trip(self, records, imei):
        import datetime
        get_time_zone = self.get_time_zone(imei)
        time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

        user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).first()
        if user_trip:
            user_trip.delete()
            self.delete_measurment(user_trip.measure_id)

        last_send_time = ''
        last_mileage = 0
        distance = 0
        time = 0
        last_lat = ''
        last_long = ''
        trip_log = []

        records = sorted(records, key = lambda i: i['send_time'],reverse=False)

        for record in records:
            if record.get('report_name', None):
                details = record
                details['send_time'] = str(record['send_time'])
                if details.get('gps_accuracy') not in ['0', 0] and float(details.get('mileage'))!=last_mileage and float(details.get('mileage'))>last_mileage and details.get('mileage', None) and details.get('latitude', None) != 0 and details.get('longitude', None) != 0:
                    if not trip_log:
                        last_send_time = str(details.get('send_time'))
                        last_mileage = float(details.get('mileage'))
                        trip_log.append(details)
                    else:
                        if last_lat != details.get('latitude') and last_long != details.get('longitude'):
                            mean_time_diff = self.make_time_diff(last_send_time, str(details.get('send_time')))
                            # trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                            # trip_log = []
                            # distance = 0
                            # trip_log.append(details)
                            # last_send_time = str(details.get('send_time'))
                            # last_mileage = float(details.get('mileage'))
                            # time = 0

                            try:
                                average_time_diff = mean_time_diff/60
                            except(Exception) as e:
                                average_time_diff = 0

                            if average_time_diff > 15:
                                trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                                # time.sleep(1)
                                distance = 0
                                time = 0
                                trip_log = []
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))
                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')
                            else:
                                distance += float(details.get('mileage')) - last_mileage
                                time += mean_time_diff
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))

                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')
                        else:
                            print('not matching')
                            pass
                                

                elif ('+RESP:GTSTT' in details.get('report_name', None) or '+BUFF:GTSTT' in details.get('report_name', None)) and details.get('latitude', None) != 0 and details.get('longitude', None) != 0 and float(details.get('mileage'))>=last_mileage:
                    if details.get('state', None) == 42 or details.get('state', None) == 22:
                        if not trip_log:
                            last_send_time = str(details.get('send_time'))
                            last_mileage = float(details.get('mileage'))
                            trip_log.append(details)
                        else:
                            trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                            # time.sleep(1)
                            trip_log = []
                            distance = 0
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
                            # time.sleep(1)
                            last_send_time = None
                            last_mileage = 0
                            distance = 0
                            time = 0
                            trip_log = []
                        else:
                            pass
        
        trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
        # time.sleep(1)


    def delete_measurment(self, measure_id):
        trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
        if trips_measure:
            trips_measure.delete()
        pass


    def make_time_diff(self, old_time, new_time):
        try:
            time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
                time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
        except(Exception)as e:
            print(e)
            time_diff = 0
        return time_diff


    def get_time_zone(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        if sub:
            try:
                user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
                if user:
                    return user.time_zone
            except(Exception)as e:
                print(e)
                return None
        return None

    def transfer_to_trip(self, imei, total_distance, total_time, log, start_time=None, end_time=None):
        import datetime
        get_time_zone = self.get_time_zone(imei)
        time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

        # print(log)
        if total_distance >= 0.1:
            user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).first()
            if user_trip:
                self.trip_id = user_trip.id

                if total_distance>0:
                    check_last_trip = user_trip.trip_log[-1]
                    current_log = log[0]
                    time_diff, time_diff_status = self.check_time_diff(imei, str(check_last_trip[-1].get('send_time')), str(current_log.get('send_time')))
                    if time_diff_status:
                        trip_to_be_update = user_trip.trip_log
                        trip_to_be_update = trip_to_be_update[-1]+log
                        user_trip.trip_log[-1] = trip_to_be_update
                        user_trip.start_time = start_time
                        user_trip.end_time = end_time
                        user_trip.save()
                        close_old_connections()
                        self.update_existing_trip_mesurement(user_trip.measure_id, total_distance, total_time, abs(time_diff))
                    else:
                        user_trip.trip_log.append(log)
                        user_trip.start_time = start_time
                        user_trip.end_time = end_time
                        user_trip.save()
                        self.update_trip_mesurement(user_trip.measure_id, total_distance, total_time)
                        # time.sleep(1)
                else:
                    pass
            else:
                time_to_save = datetime.datetime.strftime(time_timezone, "%Y-%m-%d %H:%M:%S")
                customer_id = self.get_customer_id(imei)
                user_trip_obj = {
                    'imei':imei,
                    'driver_id':'1',
                    'trip_log':[log],
                    'measure_id':10,
                    'record_date_timezone': time_to_save,
                    'start_time' : start_time,
                    'end_time' : end_time,
                    'customer_id':customer_id
                }
                # print(user_trip_obj['time_to_save'])
                serializer = UserTripSerializer(data = user_trip_obj)

                if serializer.is_valid():
                    serializer.save()
                    close_old_connections()
                    self.update_trip_mesurement(serializer.data['measure_id'], total_distance, total_time)
                    self.trip_id = serializer.data['id']
                else:
                    print(serializer.errors)
                    pass


    def get_customer_id(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        return str(sub.customer_id)

    def check_time_diff(self, imei, old_time, new_time):
        time_diff_seconds = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
            time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))

        try:
            time_diff = time_diff_seconds/60
        except(Exception) as e:
            time_diff = 0

        if time_diff>= self.get_trip_timeout(imei):
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
                    return float(setting.trip_end_timer)
                elif setting.device_frequency_value and setting.device_frequency_value > 0:
                    return float(setting.device_frequency_value)*2
                else:
                    return 15
            except(Exception)as e:
                return 15
        return 15

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






class CalculateGl24Trip30Minutes(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def do(self):
        import datetime
        self.get_imei_list()
        for i in self.imei_list:
            
            if self.check_frequency(i):
                print(i)
                timezone = self.get_time_zone(i)
                if timezone:
                    local_datetime = datetime.datetime.now(pytz.timezone(timezone))
                    date_to_flter = self.get_date_to_filter(timezone, local_datetime.day, local_datetime.month, local_datetime.year)
                    get_data = self.get_data(i, date_to_flter)
                    
                    try:
                        self.calculate_trip(get_data, i)
                    except(Exception)as e:
                        print(e)
                        pass

                    try:
                        delete_record = TripCalculationGLCron.objects.filter(imei=i).all()
                        delete_record.delete()
                    except(Exception)as e:
                        prine(e)
                        pass


    def check_frequency(self, imei):
        setting = SettingsModel.objects.filter(imei=imei).last()
        if setting:
            if setting.device_frequency_value:
                if setting.device_frequency_value >= 15:
                    return True
                return False
            return False
        return False

    def send_cron_mail_now(self):
        list_ = ",".join(self.imei_list)
        send_cron_mail_24(list_)
        pass


    def get_imei_list(self):
        self.imei_list = TripCalculationGLCron.objects.distinct(field="imei")

    def get_data(self, imei, time_date):

        # stt = SttMarkers.objects.filter(imei=imei, record_date__gte=time_date).exclude(latitude = 0, longitude = 0).all()
        try:
            send_time = int(time_date.strftime("%Y%m%d%H%M%S"))
            stt = SttMarkers.objects.filter(imei=imei, send_time__gte=send_time).exclude(latitude = 0, longitude = 0).all()
        except(Exception)as e:
            stt = SttMarkers.objects.filter(imei=imei, record_date__gte=time_date).exclude(latitude = 0, longitude = 0).all()

        stt_serializer = SttMarkersSerializer(stt, many=True).data

        try:
            send_time = int(time_date.strftime("%Y%m%d%H%M%S"))
            fri = GLFriMarkers.objects.filter(imei=imei, send_time__gte=send_time, gps_accuracy__gt=0).exclude(latitude = 0, longitude = 0, speed=0).all()
        except(Exception)as e:
            fri = GLFriMarkers.objects.filter(imei=imei, record_date__gte=time_date, gps_accuracy__gt=0).exclude(latitude = 0, longitude = 0, speed=0).all()

        
        fri_serializer = GLFriMarkersSerializer(fri, many=True).data
        data = list(stt_serializer)+list(fri_serializer)
        data = [dict(i) for i in data]
        records = sorted(data, key = lambda i: i['send_time'],reverse=False)
        return records



    def get_date_to_filter(self, timezone, day, month, year):
        timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', time_fmt)
        my_timestamp = datetime.datetime.now() # some timestamp
        old_timezone = pytz.timezone(timezone)
        new_timezone = pytz.timezone("UTC")
        my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
        return my_timestamp_in_new_timezone


    def calculate_trip(self, records, imei):
        import datetime
        get_time_zone = self.get_time_zone(imei)
        time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

        user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).first()
        if user_trip:
            user_trip.delete()
            self.delete_measurment(user_trip.measure_id)

        last_send_time = ''
        last_mileage = 0
        distance = 0
        time = 0
        last_lat = ''
        last_long = ''
        trip_log = []

        records = sorted(records, key = lambda i: i['send_time'],reverse=False)

        for record in records:
            if record.get('report_name', None):
                details = record
                details['send_time'] = str(record['send_time'])
                if details.get('gps_accuracy') not in ['0', 0] and float(details.get('mileage'))!=last_mileage and float(details.get('mileage'))>last_mileage and details.get('mileage', None) and details.get('latitude', None) != 0 and details.get('longitude', None) != 0:
                    if not trip_log:
                        last_send_time = str(details.get('send_time'))
                        last_mileage = float(details.get('mileage'))
                        trip_log.append(details)
                    else:
                        if last_lat != details.get('latitude') and last_long != details.get('longitude'):
                            mean_time_diff = self.make_time_diff(last_send_time, str(details.get('send_time')))
                            # trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                            # trip_log = []
                            # distance = 0
                            # trip_log.append(details)
                            # last_send_time = str(details.get('send_time'))
                            # last_mileage = float(details.get('mileage'))
                            # time = 0

                            try:
                                average_time_diff = mean_time_diff/60
                            except(Exception) as e:
                                average_time_diff = 0

                            if average_time_diff > 30:
                                trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                                # time.sleep(1)
                                distance = 0
                                time = 0
                                trip_log = []
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))
                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')
                            else:
                                distance += float(details.get('mileage')) - last_mileage
                                time += mean_time_diff
                                trip_log.append(details)
                                last_send_time = details.get('send_time')
                                last_mileage = float(details.get('mileage'))

                                last_long = details.get('longitude')
                                last_lat = details.get('latitude')
                        else:
                            print('not matching')
                            pass
                                

                elif ('+RESP:GTSTT' in details.get('report_name', None) or '+BUFF:GTSTT' in details.get('report_name', None)) and details.get('latitude', None) != 0 and details.get('longitude', None) != 0 and float(details.get('mileage'))>=last_mileage:
                    if details.get('state', None) == 42 or details.get('state', None) == 22:
                        if not trip_log:
                            last_send_time = str(details.get('send_time'))
                            last_mileage = float(details.get('mileage'))
                            trip_log.append(details)
                        else:
                            trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
                            # time.sleep(1)
                            trip_log = []
                            distance = 0
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
                            # time.sleep(1)
                            last_send_time = None
                            last_mileage = 0
                            distance = 0
                            time = 0
                            trip_log = []
                        else:
                            pass
        
        trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
        # time.sleep(1)


    def delete_measurment(self, measure_id):
        trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
        if trips_measure:
            trips_measure.delete()
        pass


    def make_time_diff(self, old_time, new_time):
        try:
            time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
                time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
        except(Exception)as e:
            print(e)
            time_diff = 0
        return time_diff


    def get_time_zone(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        if sub:
            try:
                user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
                if user:
                    return user.time_zone
            except(Exception)as e:
                print(e)
                return None
        return None

    def transfer_to_trip(self, imei, total_distance, total_time, log, start_time=None, end_time=None):
        import datetime
        get_time_zone = self.get_time_zone(imei)
        time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

        # print(log)
        if total_distance >= 0.1:
            user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).first()
            if user_trip:
                self.trip_id = user_trip.id

                if total_distance>0:
                    check_last_trip = user_trip.trip_log[-1]
                    current_log = log[0]
                    time_diff, time_diff_status = self.check_time_diff(imei, str(check_last_trip[-1].get('send_time')), str(current_log.get('send_time')))
                    if time_diff_status:
                        trip_to_be_update = user_trip.trip_log
                        trip_to_be_update = trip_to_be_update[-1]+log
                        user_trip.trip_log[-1] = trip_to_be_update
                        user_trip.start_time = start_time
                        user_trip.end_time = end_time
                        user_trip.save()
                        close_old_connections()
                        self.update_existing_trip_mesurement(user_trip.measure_id, total_distance, total_time, abs(time_diff))
                    else:
                        user_trip.trip_log.append(log)
                        user_trip.start_time = start_time
                        user_trip.end_time = end_time
                        user_trip.save()
                        self.update_trip_mesurement(user_trip.measure_id, total_distance, total_time)
                        # time.sleep(1)
                else:
                    pass
            else:
                time_to_save = datetime.datetime.strftime(time_timezone, "%Y-%m-%d %H:%M:%S")
                customer_id = self.get_customer_id(imei)
                user_trip_obj = {
                    'imei':imei,
                    'driver_id':'1',
                    'trip_log':[log],
                    'measure_id':10,
                    'record_date_timezone': time_to_save,
                    'start_time' : start_time,
                    'end_time' : end_time,
                    'customer_id':customer_id
                }
                # print(user_trip_obj['time_to_save'])
                serializer = UserTripSerializer(data = user_trip_obj)

                if serializer.is_valid():
                    serializer.save()
                    close_old_connections()
                    self.update_trip_mesurement(serializer.data['measure_id'], total_distance, total_time)
                    self.trip_id = serializer.data['id']
                else:
                    print(serializer.errors)
                    pass


    def get_customer_id(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        return str(sub.customer_id)

    def check_time_diff(self, imei, old_time, new_time):
        time_diff_seconds = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
            time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))

        try:
            time_diff = time_diff_seconds/60
        except(Exception) as e:
            time_diff = 0

        if time_diff>= 30: #self.get_trip_timeout(imei):
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
                    return float(setting.trip_end_timer)
                elif setting.device_frequency_value and setting.device_frequency_value > 0:
                    return float(setting.device_frequency_value)*2
                else:
                    return 30
            except(Exception)as e:
                return 30
        return 30

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