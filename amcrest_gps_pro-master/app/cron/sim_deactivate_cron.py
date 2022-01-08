from django_cron import CronJobBase, Schedule

import json
import datetime
import time
import pytz
from app.serializers import *

from app.models import *
from services.models import *
from services.sim_update_service import *

time_fmt = '%Y-%m-%d %H:%M:%S'

class SimDeactivateCron(CronJobBase):
    RUN_EVERY_MINS = 0 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.sim_deactivate_cron'    # a unique code

    def do(self):
        iccids = []
        get_api_key = self.get_api_key()
        try:
            # sim_details = PodSimCron.objects.filter(date__day=datetime.datetime.now().day, date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).all()
            sim_details = PodSimCron.objects.filter(date__lte=datetime.datetime.now()).all()
            for sim_detail in sim_details:
                iccids.append(sim_detail.iccid)
                deativate_pod_sim_immeidiate(sim_detail.iccid)
                self.update_device_listing(sim_detail.iccid)
                sim_detail.delete()
                # break
        except(Exception)as e:
            print(e)
            pass

        self.send_mail(iccids)

    	
    	
    def get_api_key(self):
        api_key = SimUpdateCredentials.objects.filter(key_name='pod_credentials').first()
        return api_key.api_key


    def update_device_listing(self, iccid):
        subscription = Subscription.objects.filter(imei_iccid = iccid).last()
        if subscription:
            subscription.device_listing = False
            subscription.sim_status = False
            subscription.subscription_status = 'Expired'
            subscription.save()

    def send_mail(self, iccids):
        list_ = ",".join(iccids)
        daily_pod_sim_cron(list_)
        pass

