from django_cron import CronJobBase, Schedule

import json
import datetime
import time
import pytz
from app.serializers import *

from app.models import *
from services.models import *
from services.sim_update_service import *

from services.mail_sender import *

time_fmt = '%Y-%m-%d %H:%M:%S'



class DeviceListingCronMachine(CronJobBase):
    RUN_EVERY_MINS = 0

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.device_listing_cron'

    def do(self):
        iccid = []
        try:
            # device_listing = DeviceListingCron.objects.filter(date__day=datetime.datetime.now().day, date__month=datetime.datetime.now().month, date__year=datetime.datetime.now().year).all()
            device_listing = DeviceListingCron.objects.filter(date__lte=datetime.datetime.now()).all()
            for device in device_listing:
                self.update_device_listing(device.iccid)
                iccid.append(device.iccid)
                device.delete()
        except(Exception)as e:
            print(e)

        self.send_mail(iccid)

        pass


    def update_device_listing(self, iccid):
        subscription = Subscription.objects.filter(imei_iccid = iccid).last()
        if subscription:
            subscription.device_listing = False
            subscription.save()

    def send_mail(self, iccids):
        list_ = ",".join(iccids)
        send_device_listing_cron_mail(list_)
        pass



class SubscriptionCancelCronMachine(CronJobBase):
    RUN_EVERY_MINS = 0

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.subscription_cancel'

    def do(self):
        iccid = []
        try:
            device_listing = SubscriptionCancelation.objects.filter(end_date__day=datetime.datetime.now().day, end_date__month=datetime.datetime.now().month, end_date__year=datetime.datetime.now().year).all()
            for device in device_listing:
                self.update_device_listing(device.subscription_id)
                device.delete()
        except(Exception)as e:
            print(e)

        self.send_mail(iccid)

        pass


    def update_device_listing(self, subscription_id):
        subscription = Subscription.objects.filter(subscription_id = subscription_id).last()
        if subscription:
            subscription.device_listing = False
            subscription.is_active = False
            subscription.subscription_status = 'Expired'
            subscription.save()
