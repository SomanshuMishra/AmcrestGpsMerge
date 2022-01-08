from django_cron import CronJobBase, Schedule
import json
from datetime import timedelta
import datetime
import time
import pytz
import _thread
import datedelta

import pandas as pd

from django.db.models.signals import post_save as ps
from django.dispatch import receiver
from django.db import close_old_connections
from django.contrib.auth import get_user_model
from django.db.models import Q

from app.models import *
from app.serializers import *

from app.engine_notification.notification_maker import *
from app.trip_notification import trip_notification_maker

from listener.models import *
from listener.serializers import *

from app.events.trips import trip_event_module

from services.mail_sender import *

User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'



class FuelEconomyNewCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def do(self):
        import datetime
        # imeis = ['861971050033117']

        imeis = self.get_imei()
        try:
            self.send_cron_mail_now(imeis)
        except(Exception)as e:
            print(e)

        for i in imeis:
            timezone = self.get_time_zone(i)
            fuel_capacity = self.get_tank_capacity(i)
            if fuel_capacity:
                tank_capacity_perc = fuel_capacity/100
                if timezone:
                    previous_fuel_level_instance = FuelLevelTracker.objects.filter(imei=i).last()
                    local_datetime = datetime.datetime.now(pytz.timezone(timezone)) - timedelta(days=1)
                    start_date_to_flter, end_date_to_filter = self.get_date_to_filter(timezone, local_datetime.day, local_datetime.month, local_datetime.year)
                    data_frame = self.get_records(i, start_date_to_flter, end_date_to_filter)
                    # print(data_frame)
                    prev_mileage = None
                    prev_fuel_level = None

                    if previous_fuel_level_instance:
                        try:
                            prev_mileage = previous_fuel_level_instance.end_mileage
                            prev_fuel_level = previous_fuel_level_instance.end_fuel_level
                            for index, row in data_frame.iterrows():
                                if row['obd_connection'] != 0:
                                    if row['mileage'] != 0 or row['mileage'] > prev_mileage:
                                        if row['fuel_level_input'] > prev_fuel_level + 10:
                                            previous_fuel_level_instance.end_mileage = prev_mileage
                                            previous_fuel_level_instance.end_fuel_level = prev_fuel_level
                                            previous_fuel_level_instance.updated_on = datetime.datetime.now()
                                            previous_fuel_level_instance.save()
                                            self.calculate_economy(previous_fuel_level_instance, tank_capacity_perc, local_datetime)
                                            previous_fuel_level_instance.end_mileage = row['mileage']
                                            previous_fuel_level_instance.end_fuel_level = row['fuel_level_input']
                                            previous_fuel_level_instance.start_mileage = row['mileage']
                                            previous_fuel_level_instance.start_fuel_level = row['fuel_level_input']
                                            previous_fuel_level_instance.updated_on = datetime.datetime.now()
                                            previous_fuel_level_instance.save()

                                            prev_mileage = row['mileage']
                                            prev_fuel_level = row['fuel_level_input']
                                        else:
                                            prev_mileage = row['mileage']
                                            prev_fuel_level = row['fuel_level_input']
                                    else:
                                        previous_fuel_level_instance.end_mileage = row['mileage']
                                        previous_fuel_level_instance.end_fuel_level = row['fuel_level_input']
                                        previous_fuel_level_instance.start_mileage = row['mileage']
                                        previous_fuel_level_instance.start_fuel_level = row['fuel_level_input']
                                        previous_fuel_level_instance.updated_on = datetime.datetime.now()
                                        previous_fuel_level_instance.save()

                                        prev_mileage = row['mileage']
                                        prev_fuel_level = row['fuel_level_input']
                            self.update_lower_limit(i, prev_fuel_level, prev_mileage)
                        except(Exception)as e:
                            print(e)
                            send_error_mail('Fuel Economy cron error', 'Error :'+str(e)+' '+str(i))
                            pass
                    else:   
                        try:
                            inserted = False
                            for index, row in data_frame.iterrows():
                                if row['obd_connection'] != 0:
                                    if prev_fuel_level:
                                        if row['fuel_level_input'] > prev_fuel_level + 10:
                                            if not inserted:
                                                self.insert_upper_limit(i, row['fuel_level_input'], row['mileage'])
                                                inserted = True
                                                prev_fuel_level = row['fuel_level_input']
                                                prev_mileage = row['mileage']
                                            else:
                                                previous_fuel_level_instance = FuelLevelTracker.objects.filter(imei=i).last()
                                                if previous_fuel_level_instance:
                                                    if prev_mileage < row['mileage']:
                                                        previous_fuel_level_instance.end_mileage = prev_mileage
                                                        previous_fuel_level_instance.end_fuel_level = prev_fuel_level
                                                        previous_fuel_level_instance.updated_on = datetime.datetime.now()
                                                        previous_fuel_level_instance.save()
                                                        self.calculate_economy(previous_fuel_level_instance, tank_capacity_perc, local_datetime)

                                                        previous_fuel_level_instance.end_mileage = row['mileage']
                                                        previous_fuel_level_instance.end_fuel_level = row['fuel_level_input']
                                                        previous_fuel_level_instance.start_mileage = row['mileage']
                                                        previous_fuel_level_instance.start_fuel_level = row['fuel_level_input']
                                                        previous_fuel_level_instance.updated_on = datetime.datetime.now()
                                                        previous_fuel_level_instance.save()

                                                        prev_fuel_level = row['fuel_level_input']
                                                        prev_mileage = row['mileage']
                                                    else:
                                                        previous_fuel_level_instance.end_mileage = row['mileage']
                                                        previous_fuel_level_instance.end_fuel_level = row['fuel_level_input']
                                                        previous_fuel_level_instance.start_mileage = row['mileage']
                                                        previous_fuel_level_instance.start_fuel_level = row['fuel_level_input']
                                                        previous_fuel_level_instance.updated_on = datetime.datetime.now()
                                                        previous_fuel_level_instance.save()
                                                        
                                                        prev_fuel_level = row['fuel_level_input']
                                                        prev_mileage = row['mileage']
                                                else:
                                                    self.insert_upper_limit(i, row['fuel_level_input'], row['mileage'])
                                                    inserted = True
                                                    prev_fuel_level = row['fuel_level_input']
                                                    prev_mileage = row['mileage']
                                        else:
                                            prev_fuel_level = row['fuel_level_input']
                                            prev_mileage = row['mileage']
                                    else:
                                        prev_fuel_level = row['fuel_level_input']
                                        prev_mileage = row['mileage']

                            self.update_lower_limit(i, prev_fuel_level, prev_mileage)
                        except(Exception)as e:
                            print(e)
                            send_error_mail('Fuel Economy cron error', 'Error :'+str(e)+' '+str(i))
                        

    def calculate_economy(self, fuel_tracker, tank_capacity_perc, local_datetime):
        fuel_level = fuel_tracker.start_fuel_level - fuel_tracker.end_fuel_level
        mileage = fuel_tracker.end_mileage - fuel_tracker.start_mileage
        fuel_perc = tank_capacity_perc*fuel_level
        fuel_economy = (mileage/1.609)/fuel_perc
        kml_fuel_economy = fuel_economy*0.425143707

        existing_fuel = FuelEconomy.objects.filter(imei=fuel_tracker.imei,record_date__day=local_datetime.day, record_date__month=local_datetime.month, record_date__year=local_datetime.year).last()
        if existing_fuel:
            existing_fuel.delete()

        serializer = FuelEconomySerializer(data={
            "imei" : fuel_tracker.imei,
            "fuel_economy" : kml_fuel_economy,
            "record_date" : local_datetime.date(),
            "customer_id" : self.get_customer_id(fuel_tracker.imei)
            })

        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors, 'errors---------------')
        pass


    def get_imei(self):
        imeis = []
        date_to_filter = datetime.datetime.now()-timedelta(days=1)
        from_date = str(date_to_filter.year)+'-'+str(date_to_filter.month)+'-'+str(date_to_filter.day)+' 00:00:00'
        to_date = str(date_to_filter.year)+'-'+str(date_to_filter.month)+'-'+str(date_to_filter.day)+' 23:59:59'
        trips = UserObdTrip.objects.filter(record_date_timezone__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S'), record_date_timezone__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all()
        
        imeis = [i.imei for i in trips]
        imeis = list(set(imeis))
        
        return imeis

    def get_tank_capacity(self, imei):
        tank_capacity = SettingsModel.objects.filter(imei=imei).last()
        if tank_capacity:
            if tank_capacity.fuel_capacity:
                return tank_capacity.fuel_capacity
            return None
        return None

    def insert_upper_limit(self, imei, upper_fuel_level, mileage):
        fuel_level = FuelLevelTracker(
            imei = imei,
            start_mileage = mileage,
            start_fuel_level = upper_fuel_level,
            end_mileage = mileage,
            end_fuel_level = upper_fuel_level
            )

        fuel_level.save()
        pass


    def update_upper_limit(self, imei, upper_fuel_level, mileage, fuel_level_track):
        fuel_level_track.start_fuel_level = upper_fuel_level
        fuel_level_track.start_mileage = mileage
        fuel_level_track.updated_on = datetime.datetime.now()
        fuel_level_track.save()


    def update_lower_limit(self, imei, lower_fuel_level, mileage):
        FuelLevelTracker.objects.filter(imei=imei).update(end_mileage=mileage, end_fuel_level=lower_fuel_level, updated_on=datetime.datetime.now())



    def send_cron_mail_now(self, imei_list):
        list_ = ",".join(imei_list)
        send_cron_mail_fuel_economy(list_)
        pass

    def get_records(self, imei, start_time, end_time):
        start_send_time = int(start_time.strftime("%Y%m%d%H%M%S"))
        end_send_time = int(end_time.strftime("%Y%m%d%H%M%S"))

        obd = ObdMarkers.objects.filter(imei=imei, send_time__gte=start_send_time, send_time__lte=end_send_time, fuel_level_input__isnull=False, mileage__isnull=False, engine_coolant_temp__isnull=False).order_by('send_time').values('fuel_level_input','obd_mileage', 'mileage', 'send_time', 'imei', 'obd_connection').all()
        df = pd.DataFrame(list(obd))
        pd.set_option('display.max_rows', df.shape[0]+1)
        # print(df)
        return df

    def get_date_to_filter(self, timezone, day, month, year):
        timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', time_fmt)
        my_timestamp = datetime.datetime.now() # some timestamp
        old_timezone = pytz.timezone(timezone)
        new_timezone = pytz.timezone("UTC")
        my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)

        end_timestamp = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', time_fmt)
        end_my_timestamp = datetime.datetime.now() # some timestamp
        end_old_timezone = pytz.timezone(timezone)
        end_new_timezone = pytz.timezone("UTC")
        end_my_timestamp_in_new_timezone = end_old_timezone.localize(end_timestamp).astimezone(end_new_timezone)
        return my_timestamp_in_new_timezone, end_my_timestamp_in_new_timezone

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



    def get_customer_id(self, imei):
        sub = Subscription.objects.filter(imei_no=imei).last()
        return str(sub.customer_id)
