from django_cron import CronJobBase, Schedule

import json
# import datetime
import time
import pytz
from app.serializers import *

from app.models import *
from services.models import *
from services.sim_update_service import *
from listener.models import *

from datetime import datetime, timedelta



time_fmt = '%Y-%m-%d %H:%M:%S'

class DriverScoreMchine(CronJobBase):
    RUN_EVERY_MINS = 0 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.driver_score'    # a unique code

    def do(self):
        time_threshold = datetime.now() - timedelta(hours=10)
        results = ObdMarkers.objects.filter(record_date__gte=time_threshold).values('imei').distinct()
        
        for i in results:
            timezone = self.get_time_zone(i.get('imei'))
            if timezone:
                user_time = datetime.now(pytz.timezone(timezone))
                harsh_score = self.harsh_score(i.get('imei'), user_time.date())
                speed_score = self.speed_score(i.get('imei'), user_time.date())
                idle_time_score = self.idle_time_score_calculator(i.get('imei'), user_time.date())

                total_score = (harsh_score+speed_score+idle_time_score)/3
                try:
                    customer_id = self.get_customer_id(i.get('imei'))
                except(Exception)as e:
                    customer_id = None

                self.save_score(i.get('imei'), customer_id, total_score, user_time.date())

    def save_score(self,imei, customer_id, total_score, date):
        delete_score = DriverScore.objects.filter(imei=imei, record_date=date).all()
        if delete_score:
            delete_score.delete()
            
        score_to_save = {
            'imei':imei,
            "driver_score":round(total_score, 2),
            'record_date':date,
            'customer_id':customer_id
        }

        serializer = DriverScoreSerializer(data=score_to_save)
        if serializer.is_valid():
            serializer.save()

    def get_customer_id(self, imei):
        customer_id = Subscription.objects.filter(imei_no=imei).last()
        close_old_connections()
        if customer_id:
            return customer_id.customer_id
        return None
                
    def harsh_score(self, imei, date):
        harsh_notification_score = 100
        harsh = HarshBehaviourEvent.objects.filter(record_date=date, imei=imei)
        harsh_notification_score = 100 - (len(harsh)*0.5)
        return harsh_notification_score

    def speed_score(self, imei, date):
        import datetime
        speed_notification_score = 0
        try:
            record_date_gte = datetime.datetime.strptime(str(date.year)+"-"+str(date.month)+"-"+str(date.day)+" 00:00:00", "%Y-%m-%d %H:%M:%S")
            record_date_lte = datetime.datetime.strptime(str(date.year)+"-"+str(date.month)+"-"+str(date.day)+" 23:59:59", "%Y-%m-%d %H:%M:%S")
            notifications = Notifications.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, type='speed').all()
            speed_notification_score = 100 - (len(notifications)*0.3)
        except(Exception)as e:
            print(e)
            pass
        return speed_notification_score

    def idle_time_score_calculator(self, imei, date):
        import datetime
        idle_time_score = 100
        try:
            record_date_gte = datetime.datetime.strptime(str(date.year)+"-"+str(date.month)+"-"+str(date.day)+" 00:00:00", "%Y-%m-%d %H:%M:%S")
            record_date_lte = datetime.datetime.strptime(str(date.year)+"-"+str(date.month)+"-"+str(date.day)+" 23:59:59", "%Y-%m-%d %H:%M:%S")
            user_trip = UserObdTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).first()
            
            start_trip_time = user_trip.trip_log[0][0].get('send_time')
            end_trip_time = user_trip.trip_log[-1][-1].get('send_time')

            _date = {
                'start':user_trip.trip_log[0][0].get('send_time'),
                'end':user_trip.trip_log[-1][-1].get('send_time')
            }
            idle_time  = self.idle_time(_date, imei)
            total_travelling_time = self.get_total_travelling_time(user_trip.trip_log)

            total_travelling_time_per = total_travelling_time/100
            idle_time_per = idle_time/total_travelling_time_per
            idle_time_score = 100-self.get_idle_score_cal_value(idle_time_per)
        except(Exception)as e:
            print(e)
        return idle_time_score

    def get_idle_score_cal_value(self, percentage):

        if percentage<30:
            return 0

        if percentage>30 and percentage<=40:
            return 2.5

        if percentage>40 and percentage<=50:
            return 2.5*2

        if percentage>50 and percentage<=60:
            return 2.5*3

        if percentage>60 and percentage<=70:
            return 2.5*4

        if percentage>70 and percentage<=80:
            return 2.5*5

        if percentage>80 and percentage<=90:
            return 2.5*6

        if percentage>90 and percentage<=100:
            return 2.5*7

    def get_total_travelling_time(self, trip_log):
        total_time = 0
        for trip in trip_log:
            old_time = str(trip[0].get('send_time'))
            new_time = str(trip[-1].get('send_time'))

            try:
                time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
                    time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
            except(Exception)as e:
                time_diff = 0

            total_time = total_time+time_diff
        return total_time



    def idle_time(self, date, imei):
        start_idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), protocol='+RESP:GTIDN', imei=imei).all()
        end_idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), protocol='+RESP:GTIDF', imei=imei).all()
        
        total_time = 0
        for i in range(len(start_idle_records)):

            try:
                start_time = start_idle_records[0]
                end_time = end_idle_records[0]
            except(Exception)as e:
                pass

            try:
                new_time = str(end_time.send_time)
                old_time = str(start_time.send_time)
            except(Exception)as e:
                pass

            try:
                time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
                    time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
            except(Exception)as e:
                time_diff = 0

            total_time = total_time+time_diff
        return total_time


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

# record_date_gte = datetime.datetime.strptime(from_date[2]+"-"+from_date[1]+"-"+from_date[0]+" 00:00:00", "%Y-%m-%d %H:%M:%S")