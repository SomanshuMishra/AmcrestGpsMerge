from listener.models import *
from listener.serializers import *

from services.mail_sender import *

from django_cron import CronJobBase, Schedule
# '1760277'

records = [[1000001, 1100000], [1100001, 1200000], [1200001, 1300000], [1300001, 1400000], [1400001, 1500000],
			[1500001, 1600000], [1600001, 1700000], [1700001, 1800000], [1800001, 1900000]]

# records = [[600001, 700000], [700001, 800000], [800001, 900000], [900001, 1000000]]

class DataCorrectorCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'listener.cron.data_updator'

    def do(self):
        import datetime

      #   for i in records:
      #   	subject = 'Data Updating from {} to {}'.format(i[0], i[1])
      #   	message = 'Data Updating from {} to {}'.format(i[0], i[1])
      #   	cron_mail_sender(subject, message)
	     #    gl_fri = GLFriMarkersBackup.objects.all()[i[0]:i[1]]

	     #    for gl in gl_fri:
	     #    	temp = {
			   #      	"report_name": "+RESP:GTFRI",
						# "device_name": None,
						# "report_id": gl.device_name,
						# "report_type": gl.report_id,
						# "number" : gl.report_type,
						# "gps_accuracy": gl.number,
						# "speed" : gl.gps_accuracy,
						# "azimuth" : gl.speed,
						# "altitude":gl.azimuth,
						# "longitude" : gl.altitude,
						# "latitude" : gl.longitude,
						# "gps_utc_time":gl.latitude,
						# "mcc":gl.gps_utc_time,
						# "mnc": gl.mcc,
						# "lac":gl.mnc,
						# "ceil_id":gl.lac,
						# "mileage":gl.ceil_id,
						# "battery_percentage":gl.mileage,
						# "send_time":gl.latitude,
						# "tail":gl.send_time,
						# "location_status":None
	        	    
	     #    	}
	     #    	save_serializers = GLFriMarkersBackupSerializer(gl, data=temp)
	     #    	if save_serializers.is_valid():
	     #    	    save_serializers.save()
	     #    	else:
	     #    	    print(save_serializers.errors)