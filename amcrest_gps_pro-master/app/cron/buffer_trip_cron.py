from django_cron import CronJobBase, Schedule
import json
import datetime
from datetime import timedelta
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


class BufferTripCalculation:

    def start(self):
    	get_last_buff_imei = self.get_imei()
    	print(get_last_buff_imei)
    	for imei in get_last_buff_imei:
    		timezone = self.get_time_zone(imei.get('imei'))
    		if timezone:
    			yesterday = self.get_current_user_time(timezone)
    			self.get_date_to_filter(timezone, yesterday.day, yesterday.month, yesterday.year)
    			get_data = self.get_data(imei.get('imei'))
    			try:
    				self.calculate_trip(get_data, imei.get('imei'))
    			except(Exception)as e:
    				print(e)
    				pass

    def get_imei(self):
    	today = datetime.datetime.now().date()
    	last_date = datetime.datetime.now() - datetime.timedelta(days = 1)
    	last_date = last_date.date()
    	fri = ObdMarkers.objects.filter(record_date__range=[last_date, today], gps_accuracy__gt=0, protocol="+RESP:GTOBD").values('imei').distinct()
    	return fri

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

    def get_current_user_time(self, timezone):
    	new_timezone = pytz.timezone(timezone)
    	old_timezone = pytz.timezone("UTC")
    	my_timestamp = datetime.datetime.now()
    	current_user_time = old_timezone.localize(my_timestamp).astimezone(new_timezone)
    	yesterday = current_user_time.date() - timedelta(days = 1)
    	return yesterday

    def get_data(self, imei):
    	ignition = IgnitionOnoff.objects.filter(imei=imei, record_date__range=[self.timestamp_start, self.timestamp_end]).all()
    	ignition_serializer = IgnitionOnoffSerializer(ignition, many=True).data
    	obd = ObdMarkers.objects.filter(imei=imei, record_date__range=[self.timestamp_start, self.timestamp_end]).all()
    	obd_serializer = ObdMarkersSerializer(obd, many=True).data
    	# data = list(ignition_serializer)+list(obd_serializer)
    	# records = sorted(data, key = lambda i: i['send_time'],reverse=False)
    	data = list(ignition_serializer)+list(obd_serializer)
    	data = [dict(i) for i in data]
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
    	get_time_zone = self.get_time_zone(imei)
    	time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
    	user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=self.user_end_time, record_date_timezone__gte=self.user_start_time).first()
    	if user_trip:
    		user_trip.delete()
    		self.delete_measurment(user_trip.measure_id)

    	last_send_time = ''
    	last_mileage = 0
    	distance = 0
    	time = 0
    	trip_log = []
    	records = sorted(records, key = lambda i: i['send_time'],reverse=False)
    	for record in records:
    		if record.get('protocol', None) and record.get('mileage'):
    			details = record
    			details['send_time'] = str(record['send_time'])
    			if float(details.get('mileage'))!=last_mileage and details.get('protocol', None) == '+RESP:GTOBD':
    				if not trip_log:
    					last_send_time = str(details.get('send_time'))
    					last_mileage = float(details.get('mileage'))
    					trip_log.append(details)
    				else:
    					distance += float(details.get('mileage')) - last_mileage
    					time += self.make_time_diff(last_send_time, str(details.get('send_time')))
    					trip_log.append(details)
    					last_send_time = details.get('send_time')
    					last_mileage = float(details.get('mileage'))

    			elif details.get('protocol', None) == '+RESP:GTIGN' or details.get('protocol', None) == '+RESP:GTIGF':
    				if details.get('protocol', None) == '+RESP:GTIGN':
    					if not trip_log:
    						last_send_time = str(details.get('send_time'))
    						last_mileage = float(details.get('mileage'))
    						trip_log.append(details)
    					else:
    						trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
    						trip_log = []
    						distance = 0
    						trip_log.append(details)
    						last_send_time = str(details.get('send_time'))
    						last_mileage = float(details.get('mileage'))
    						time = 0

    				elif details.get('protocol', None) == '+RESP:GTIGF':
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
    	trip_c = self.transfer_to_trip(imei, distance, time, trip_log)

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
    			return None
    	return None

    def transfer_to_trip(self, imei, total_distance, total_time, log, start_time=None, end_time=None):
        import datetime
        get_time_zone = self.get_time_zone(imei)
        time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
        from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
        to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'
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
                        time.sleep(1)
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

    	# print(time_diff_seconds)
    	try:
    		time_diff = time_diff_seconds/60
    	except(Exception) as e:
    		# print(e)
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
    	trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).last()
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






# class BufferTripCalculation:
# 	def start(self):
# 		get_last_buff_imei = self.get_imei()
# 		print(get_last_buff_imei)
# 		for imei in get_last_buff_imei:
# 			timezone = self.get_time_zone(imei.get('imei'))
# 			if timezone:
# 				yesterday = self.get_current_user_time(timezone)
# 				self.get_date_to_filter(timezone, yesterday.day, yesterday.month, yesterday.year)
				
# 				get_data = self.get_data(imei.get('imei'))

# 				try:
# 					self.calculate_trip(get_data, imei.get('imei'))
# 				except(Exception)as e:
# 					print(e)
# 					pass



# 	def get_imei(self):
# 		today = datetime.datetime.now().date()
# 		last_date = datetime.datetime.now() - datetime.timedelta(days = 1)
# 		last_date = last_date.date()
# 		fri = GLFriMarkers.objects.filter(record_date__range=[last_date, today], gps_accuracy__gt=0, report_name="+BUFF:GTFRI").values('imei').distinct()
# 		return fri

# 	def get_time_zone(self, imei):
# 		sub = Subscription.objects.filter(imei_no=imei).last()
# 		if sub:
# 			try:
# 				user = User.objects.filter(customer_id=sub.customer_id).first()
# 				if user:
# 					return user.time_zone
# 			except(Exception)as e:
# 				print(e)
# 				return None
# 		return None

# 	def get_current_user_time(self, timezone):
# 		new_timezone = pytz.timezone(timezone)
# 		old_timezone = pytz.timezone("UTC")
# 		my_timestamp = datetime.datetime.now()
# 		current_user_time = old_timezone.localize(my_timestamp).astimezone(new_timezone)
# 		yesterday = current_user_time.date() - timedelta(days = 1)
# 		return yesterday


# 	def get_data(self, imei):
# 		stt = SttMarkers.objects.filter(imei=imei, record_date__range=[self.timestamp_start, self.timestamp_end]).all()
# 		stt_serializer = SttMarkersSerializer(stt, many=True).data
# 		fri = GLFriMarkers.objects.filter(imei=imei, record_date__range=[self.timestamp_start, self.timestamp_end], gps_accuracy__gt=0).all()
# 		fri_serializer = GLFriMarkersSerializer(fri, many=True).data
# 		data = list(stt_serializer)+list(fri_serializer)
# 		data = [dict(i) for i in data]
# 		records = sorted(data, key = lambda i: i['send_time'],reverse=False)
# 		return records



# 	def get_date_to_filter(self, timezone, day, month, year):
# 		timestamp_start = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', time_fmt)
# 		timestamp_end = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', time_fmt)
# 		my_timestamp = datetime.datetime.now() # some timestamp
# 		old_timezone = pytz.timezone(timezone)
# 		new_timezone = pytz.timezone("UTC")
# 		self.timestamp_start = old_timezone.localize(timestamp_start).astimezone(new_timezone)
# 		self.timestamp_end = old_timezone.localize(timestamp_end).astimezone(new_timezone)

# 		self.user_start_time = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:01', time_fmt)
# 		self.user_end_time = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', time_fmt)



# 	def calculate_trip(self, records, imei):
# 		import datetime
# 		get_time_zone = self.get_time_zone(imei)
# 		time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
# 		from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
# 		to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'

# 		user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=self.user_end_time, record_date_timezone__gte=self.user_start_time).first()
# 		if user_trip:
# 			user_trip.delete()
# 			self.delete_measurment(user_trip.measure_id)

# 		last_send_time = ''
# 		last_mileage = 0
# 		distance = 0
# 		time = 0
# 		trip_log = []
# 		records = sorted(records, key = lambda i: i['send_time'],reverse=False)
# 		for record in records:
# 			if record.get('report_name', None) and record.get('mileage'):
# 				details = record
# 				details['send_time'] = str(record['send_time'])
# 				if details.get('gps_accuracy') not in ['0', 0] and float(details.get('mileage'))!=last_mileage:
# 					if not trip_log:
# 						last_send_time = str(details.get('send_time'))
# 						last_mileage = float(details.get('mileage'))
# 						trip_log.append(details)
# 					else:
# 						distance += float(details.get('mileage')) - last_mileage
# 						time += self.make_time_diff(last_send_time, str(details.get('send_time')))
# 						trip_log.append(details)
# 						last_send_time = details.get('send_time')
# 						last_mileage = float(details.get('mileage'))

# 				elif details.get('report_name', None) == '+RESP:GTSTT' or details.get('report_name', None) == '+BUFF:GTSTT':
# 					if details.get('state', None) == 42 or details.get('state', None) == 22:
# 						if not trip_log:
# 							last_send_time = str(details.get('send_time'))
# 							last_mileage = float(details.get('mileage'))
# 							trip_log.append(details)
# 						else:
# 							trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
# 							trip_log = []
# 							distance = 0
# 							trip_log.append(details)
# 							last_send_time = str(details.get('send_time'))
# 							last_mileage = float(details.get('mileage'))
# 							time = 0
# 					elif details.get('state', None) == 41 or details.get('state', None) == 21:
# 						if trip_log:
# 							distance += float(details.get('mileage')) - last_mileage
# 							time += self.make_time_diff(last_send_time, str(details.get('send_time')))
# 							trip_log.append(details)
# 							trip_c = self.transfer_to_trip(imei, distance, time, trip_log)
# 							last_send_time = None
# 							last_mileage = None
# 							distance = 0
# 							time = 0
# 							trip_log = []
# 						else:
# 							pass
# 		trip_c = self.transfer_to_trip(imei, distance, time, trip_log)

# 	def delete_measurment(self, measure_id):
# 		trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
# 		if trips_measure:
# 			trips_measure.delete()
# 		pass

# 	def make_time_diff(self, old_time, new_time):
# 		try:
# 			time_diff = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
# 				time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
# 		except(Exception)as e:
# 			time_diff = 0
# 		return time_diff
	
# 	def transfer_to_trip(self, imei, total_distance, total_time, log, start_time=None, end_time=None):
# 		import datetime
# 		get_time_zone = self.get_time_zone(imei)
# 		time_timezone = datetime.datetime.now(pytz.timezone(get_time_zone))
# 		from_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 00:00:00'
# 		to_date = str(time_timezone.year)+'-'+str(time_timezone.month)+'-'+str(time_timezone.day)+' 23:59:59'
# 		if total_distance > 0:
# 			user_trip = UserTrip.objects.filter(imei=imei, record_date_timezone__lte=self.user_end_time, record_date_timezone__gte=self.user_start_time).first()
# 			if user_trip:
# 				self.trip_id = user_trip.id
# 				if total_distance>0:
# 					check_last_trip = user_trip.trip_log[-1]
# 					current_log = log[0]
# 					time_diff, time_diff_status = self.check_time_diff(imei, str(check_last_trip[-1].get('send_time')), str(current_log.get('send_time')))
# 					if time_diff_status:
# 						trip_to_be_update = user_trip.trip_log
# 						trip_to_be_update = trip_to_be_update[-1]+log
# 						user_trip.trip_log[-1] = trip_to_be_update
# 						user_trip.start_time = start_time
# 						user_trip.end_time = end_time
# 						user_trip.save()
# 						close_old_connections()
# 						self.update_existing_trip_mesurement(user_trip.measure_id, total_distance, total_time, abs(time_diff))
# 					else:
# 						user_trip.trip_log.append(log)
# 						user_trip.start_time = start_time
# 						user_trip.end_time = end_time
# 						user_trip.save()
# 						self.update_trip_mesurement(user_trip.measure_id, total_distance, total_time)
# 				else:
# 					pass
# 			else:
# 				time_to_save = datetime.datetime.strftime(time_timezone, "%Y-%m-%d %H:%M:%S")
# 				customer_id = self.get_customer_id(imei)
# 				user_trip_obj = {
# 				'imei':imei,
# 				'driver_id':'1',
# 				'trip_log':[log],
# 				'measure_id':10,
# 				'record_date_timezone': self.user_start_time,
# 				'start_time' : start_time,
# 				'end_time' : end_time,
# 				'customer_id':customer_id
# 				}
# 				serializer = UserTripSerializer(data = user_trip_obj)
# 				if serializer.is_valid():
# 					serializer.save()
# 					close_old_connections()
# 					self.update_trip_mesurement(serializer.data['measure_id'], total_distance, total_time)
# 					self.trip_id = serializer.data['id']
# 				else:
# 					print(serializer.errors)
# 					pass

# 	def get_customer_id(self, imei):
# 		sub = Subscription.objects.filter(imei_no=imei).last()
# 		return str(sub.customer_id)

# 	def check_time_diff(self, imei, old_time, new_time):
# 		time_diff_seconds = (time.mktime(time.strptime(new_time[:4]+'-'+new_time[4:6]+'-'+new_time[6:8]+' '+new_time[-6:-4]+':'+new_time[-4:-2]+':'+new_time[-2:], time_fmt))-\
# 			time.mktime(time.strptime(old_time[:4]+'-'+old_time[4:6]+'-'+old_time[6:8]+' '+old_time[-6:-4]+':'+old_time[-4:-2]+':'+old_time[-2:], time_fmt)))
		
# 		try:
# 			time_diff = time_diff_seconds/60
# 		except(Exception) as e:
# 			time_diff = 0

# 		if time_diff>= self.get_trip_timeout(imei):
# 			return time_diff_seconds, False
# 		else:
# 			return time_diff_seconds, True

# 	def update_trip_mesurement(self, measure_id, distance, time):
# 		trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
# 		if trips_measure:
# 			trips_measure.total_distance.append(round(distance, 2))
# 			trips_measure.total_time.append(str(timedelta(seconds=time)))
# 			trips_measure.save()
# 			close_old_connections()
# 		else:
# 			trip_measure_obj = {
# 			'total_distance':[round(distance, 2)],
# 			'total_time':[str(timedelta(seconds=time))],
# 			'measure_id': measure_id
# 			}
# 			serializer = TripsMesurementSerializer(data=trip_measure_obj)
# 			if serializer.is_valid():
# 				serializer.save()
# 				close_old_connections()
# 			else:
# 				pass

# 	def get_trip_timeout(self, imei):
# 		setting = SettingsModel.objects.filter(imei=imei).last()
# 		close_old_connections()
# 		if setting:
# 			try:
# 				if setting.trip_end_timer > setting.device_frequency_value:
# 					return setting.trip_end_timer
# 				elif setting.device_frequency_value and setting.device_frequency_value > 0:
# 					return float(setting.device_frequency_value)*2
# 				else:
# 					return 10
# 			except(Exception)as e:
# 				return 10
# 		return 10
	
# 	def update_existing_trip_mesurement(self, measure_id, distance, time, time_diff):
# 		import datetime
# 		trips_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
# 		if trips_measure:
# 			distance_sum = trips_measure.total_distance[-1]

# 			try:
# 				time_sum = abs(trips_measure.total_time[-1])
# 			except(Exception)as e:
# 				time_sum = trips_measure.total_time[-1]

# 			try:
# 				time_diff = abs(time+time_diff)
# 			except(Exception)as e:
# 				time_diff = time + time_diff

# 			try:
# 				calculated_time = str(timedelta(seconds=time_diff))
# 			except(Exception)as e:
# 				calculated_time = str(timedelta(seconds=time_diff))

# 			time_sum_object = datetime.datetime.strptime(time_sum, "%H:%M:%S")
# 			calculated_time_object = datetime.datetime.strptime(calculated_time, "%H:%M:%S")
# 			time_sum_object = datetime.timedelta(hours=time_sum_object.hour, minutes=time_sum_object.minute, seconds=time_sum_object.second)
# 			calculated_time_object = datetime.timedelta(hours=calculated_time_object.hour, minutes=calculated_time_object.minute, seconds=calculated_time_object.second)
# 			trips_measure.total_distance[-1] = round(float(distance_sum)+float(distance), 2)
# 			trips_measure.total_time[-1] = str(time_sum_object+calculated_time_object)
# 			trips_measure.save()
# 			close_old_connections()