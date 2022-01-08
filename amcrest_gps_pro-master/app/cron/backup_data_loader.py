from listener.models import *
from listener.serializers import *

from services.mail_sender import *

from django_cron import CronJobBase, Schedule




import json
import time
import pytz
from app.serializers import *

from app.models import *
from services.models import *
from services.sim_update_service import *

from datetime import datetime, timedelta


class DataBackupCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def do(self):
        import datetime
        subject = 'Data Backup Cron started'
        message = 'Data Backup Cron started'
        data_backup_cron_mail_sender(subject, message)

        gl_fri = GLFriMarkers.objects.filter(send_time__gt=self.get_send_time_fri()).all()
        serializer = GLFriMarkersSerializer(gl_fri, many=True)
        for data in serializer.data:
            save_serializers = GLFriMarkersBackupSerializer(data=data)
            if save_serializers.is_valid():
                save_serializers.save()
            else:
                print(save_serializers.errors)

        stt_marker = SttMarkers.objects.filter(send_time__gt=self.get_send_time_stt()).all()
        # print(stt_marker)
        stt_serializer = SttMarkersSerializer(stt_marker, many=True)
        for data in stt_serializer.data:
            save_serializers = SttMarkersBackupSerializer(data=data)
            if save_serializers.is_valid():
                save_serializers.save()
            else:
                print(save_serializers.errors)

        subject = 'Data Backup Cron Ended'
        message = 'Data Backup Cron Ended'
        data_backup_cron_mail_sender(subject, message)


    def get_send_time_fri(self):
        gl_fri_backup = GLFriMarkersBackup.objects.last()
        if gl_fri_backup:
            return gl_fri_backup.send_time
        else:
            return 00000000000000


    def get_send_time_stt(self):
        gl_fri_backup = SttMarkersBackup.objects.last()
        if gl_fri_backup:
            return gl_fri_backup.send_time
        else:
            return 00000000000000



time_fmt = '%Y-%m-%d %H:%M:%S'

class BackupDataFlushMachine(CronJobBase):
    RUN_EVERY_MINS = 0 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.flush_data'    # a unique code

    def do(self):
        time_threshold = datetime.now() - timedelta(days=15)
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
            BatteryModel.objects.filter(record_date__lt=time_threshold).delete()
            Power.objects.filter(record_date__lt=time_threshold).delete()
            SOS.objects.filter(record_date__lt=time_threshold).delete()
            
            AlertRecords.objects.filter(record_date__lt=time_threshold).delete()
            DTCRecords.objects.filter(record_date__lt=time_threshold).delete()
        except(Exception)as e:
            print(e)
            pass

        try:
            stt_backup = SttMarkersBackup.objects.filter(record_date__lt=time_threshold).all()
            if stt_backup:
                stt_backup.delete()
        except(Exception)as e:
            pass
            


        try:
            gl_stt_backup = GLFriMarkersBackup.objects.filter(record_date__lt=time_threshold).all()
            if gl_stt_backup:
                gl_stt_backup.delete()
        except(Exception)as e:
            pass
        

class SttDataBackupCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.trip_cron'

    def __init__(self):
        self.imei_list = []
        self.trip_id = None

    def do(self):
        import datetime
        number_of_records = [[0,100000], [100000,200000], [200000,300000], [300000,400000]]
        for i in number_of_records:
            # subject = 'STT Data Inserting from {} to {}'.format(i[0], i[1])
            # message = 'STT Data Inserting from {} to {}'.format(i[0], i[1])
            # cron_mail_sender(subject, message)
            # stt_markers = SttMarkers.objects.all()[i[0]:i[1]]
            # for stt_marker in stt_markers:
            #     stt_serializer = SttMarkersSerializer(stt_marker)
            #     save_serializers = SttMarkersBackupSerializer(data=stt_serializer.data)
            #     if save_serializers.is_valid():
            #         save_serializers.save()
            #         # print('j')
            #     else:
            #         print(save_serializers.errors)

            subject = 'FRI Data Inserting from {} to {}'.format(i[0], i[1])
            message = 'FRI Data Inserting from {} to {}'.format(i[0], i[1])
            cron_mail_sender(subject, message)
            gl_fri = GLFriMarkers.objects.filter(send_time__gte=20200102231327).all()[i[0]:i[1]]

            for fri in gl_fri:
                serializer = GLFriMarkersSerializer(fri)
                save_serializers = GLFriMarkersBackupSerializer(data=serializer.data)
                if save_serializers.is_valid():
                    save_serializers.save()
                else:
                    print(save_serializers.errors)