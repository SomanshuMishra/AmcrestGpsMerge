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
from services.mail_sender import *

from datetime import datetime, timedelta



time_fmt = '%Y-%m-%d %H:%M:%S'

class DataFlushMachine(CronJobBase):
    RUN_EVERY_MINS = 0 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.flush_data'    # a unique code

    def do(self):
        time_threshold = datetime.now() - timedelta(days=3)
        dataflush_mail()
        try:
            
            AttachDettach.objects.filter(record_date__lt=time_threshold).delete()
            BatteryLow.objects.filter(record_date__lt=time_threshold).delete()
            CrashReport.objects.filter(record_date__lt=time_threshold).delete()
            EngineSummary.objects.filter(record_date__lt=time_threshold).delete()
            HarshBehaviour.objects.filter(record_date__lt=time_threshold).delete()
            IgnitionOnoff.objects.filter(record_date__lt=time_threshold).delete()
            IdleDevice.objects.filter(record_date__lt=time_threshold).delete()
            
            ObdStatusReport.objects.filter(record_date__lt=time_threshold).delete()
            SttMarkers.objects.filter(record_date__lt=time_threshold).delete()
            BatteryModel.objects.filter(record_date__lt=time_threshold).delete()
            Power.objects.filter(record_date__lt=time_threshold).delete()
            SOS.objects.filter(record_date__lt=time_threshold).delete()
            
            AlertRecords.objects.filter(record_date__lt=time_threshold).delete()
            DTCRecords.objects.filter(record_date__lt=time_threshold).delete()
        except(Exception)as e:
            print(e)
            pass

        
        try:
            glfri = GLFriMarkers.objects.filter(record_date__lt=time_threshold).values('imei').distinct()
            # print(len(glfri))
            for i in glfri:
                glfri = GLFriMarkers.objects.filter(record_date__lt=time_threshold, imei=i.get('imei')).last()
                if glfri:
                    to_delete = GLFriMarkers.objects.filter(record_date__lt=time_threshold, imei=i.get('imei'), id__lt=glfri.id).delete()
        except(Exception)as e:
            print(e)


        try:
            fir = ObdMarkers.objects.filter(record_date__lt=time_threshold).values('imei').distinct()
            # print(len(fir))
            for i in fir:
                fri = FriMarkers.objects.filter(record_date__lt=time_threshold, imei=i.get('imei')).last()
                if fri:
                    FriMarkers.objects.filter(record_date__lt=time_threshold, imei=i.get('imei'), id__lt=fri.id).delete()

                obd = ObdMarkers.objects.filter(record_date__lt=time_threshold, imei=i.get('imei')).last()
                if obd:
                    ObdMarkers.objects.filter(record_date__lt=time_threshold, imei=i.get('imei'), id__lt=obd.id).delete()
        except(Exception)as e:
            print(e)