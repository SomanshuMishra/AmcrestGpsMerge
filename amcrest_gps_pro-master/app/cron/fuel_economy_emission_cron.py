from django_cron import CronJobBase, Schedule
from django.db.models import Q
from django.db import close_old_connections


import string
import random
import json
# import datetime
import time
import pytz
import _thread
from datetime import datetime, timedelta


from app.serializers import *
from app.models import *

from listener.models import *
from listener.serializers import *

from services.models import *


from django.contrib.auth import get_user_model
User = get_user_model()

time_fmt = '%H:%M:%S'
date_fmt = '%Y-%m-%d'
date_time_fmt = '%Y-%m-%d %H:%M:%S'

from datetime import datetime, timedelta

class FuelEmissionEconomyCron(CronJobBase):
    RUN_EVERY_MINS = 0 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.flush_data'    # a unique code

    def do(self):
    	try:
    		time_threshold = datetime.now() - timedelta(hours=12)
    		user_trip = UserObdTrip.objects.filter(record_date__lte=datetime.now(), record_date__gte=time_threshold).all()

    		# user_trip = UserObdTrip.objects.filter(id='5fbeedab063e646725e96fa5').all()
    		# print(user_trip)

    		# print(user_trip)
    		# for i in user_trip:
    		# 	print(i.imei)
    		for trip in user_trip:
    			sim_mapping = SimMapping.objects.filter(imei=trip.imei).last()
    			if sim_mapping:
	    			if sim_mapping.category == 'obd':
	    				if sim_mapping.model == 'GV500' or sim_mapping.model == 'gv500':
	    					fuel_eco = FuelEconomyManualGenerate(trip.imei, trip.record_date_timezone.day, trip.record_date_timezone.month, trip.record_date_timezone.year)
	    					fuel_eco.generate()
	    				elif sim_mapping.model == 'topfly' or sim_mapping.model == 'TOPFLY':
	    					fuel_eco = FuelEventsMachine(trip.id)
	    					fuel_eco.generate()

	    					fuel_emission = EmissionMachine(trip.id)
	    					fuel_emission.receive_trip_event()
	    				else:
	    					pass
	    			else:
	    				pass
	    		else:
	    			pass
    	except(Exception)as e:
    		print(e)
    		pass
        
class FuelEventsMachine:
	def __init__(self, trip_id):
		self.trip_id = trip_id
		self.imei = None

	def generate(self):
		try:
			trip = UserObdTrip.objects.filter(id=self.trip_id).first()
		except(Exception)as e:
			trip = None

		self.imei = trip.imei
		economy = None

		if trip and self.trip_id:
			try:
				trip_logs = trip.trip_log
			except(Exception)as e:
				trip_logs = None

			print(trip_logs)

			start_trip_log = trip_logs[0]
			end_trip_log = trip_logs[-1]

			if start_trip_log[0].get('fuel_consumption'):
				start_fuel = start_trip_log[0].get('fuel_consumption')
			else:
				start_fuel = start_trip_log[1].get('fuel_consumption')


			if end_trip_log[-1].get('fuel_consumption'):
				end_fuel = end_trip_log[-1].get('fuel_consumption')
			else:
				end_fuel = end_trip_log[-2].get('fuel_consumption1')


			if start_trip_log[0].get('mileage'):
				start_mileage = start_trip_log[0].get('mileage')
			else:
				start_mileage = start_trip_log[1].get('mileage')


			if end_trip_log[-1].get('mileage'):
				end_mileage = end_trip_log[-1].get('mileage')
			else:
				end_mileage = end_trip_log[-2].get('mileage')

			try:
				fuel_consumed = (float(end_fuel) - float(start_fuel))/1000
			except(Exception)as e:
				fuel_consumed = 0


			try:
				mileage = float(end_mileage) - float(start_mileage)
			except(Exception)as e:
				mileage = 0

			try:
				hd = (1/fuel_consumed)*mileage
				economy = (1/0.264172)*hd
			except(Exception)as e:
				economy = 0


			customer_id = self.get_customer_id(self.imei)
			voltage_obj = {
				'imei': self.imei,
				'fuel_economy': economy,
				'record_date':trip.record_date_timezone.date(),
				'customer_id':customer_id
			}

			try:
				fuel_event = FuelEconomy.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)

			serializer = FuelEconomySerializer(data=voltage_obj)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()
			else:
				pass
		return economy


	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None

	def format_date(self, date):
		date_time = datetime.strptime(date[:4]+'-'+date[4:6]+'-'+date[6:8]+' '+date[-6:-4]+':'+date[-4:-2]+':'+date[-2:], date_time_fmt)
		time_zone = self.get_time_zone(self.imei)
		date_time = date_time.astimezone(pytz.timezone(time_zone))
		return date_time

	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
			close_old_connections()
			if user:
				return user.time_zone
		close_old_connections()
		return 'UTC'




class FuelEconomyManualGenerate:
	def __init__(self, imei, day, month, year):
		self.imei = imei
		self.day = day
		self.month = month
		self.year = year
		self.fuel_capacity = self.get_fuel_capacity(imei)


	def generate(self):
		timezone = self.get_time_zone(self.imei)
		fuel_economy_list = []
		fuel_emission_list = []
		final_fuel_economy = None
		if timezone:
			time_to_start, time_to_end = self.get_date_to_filter(timezone, self.day,self. month, self.year)
			data = self.get_data(self.imei, time_to_start, time_to_end)
			if self.fuel_capacity:
				for d in data:
					if d.get('journey_fuel_consumption') and d.get('trip_mileage'):
						fuel_capacity_per = (float(d.get('journey_fuel_consumption'))/100)*self.fuel_capacity
						fuel_economy_per_km = 1/fuel_capacity_per
						fuel_economy_list.append(d.get('trip_mileage')*fuel_economy_per_km)
						fuel_emission_list.append(fuel_capacity_per)
			if fuel_economy_list:
				final_fuel_economy = sum(fuel_economy_list)/len(fuel_economy_list)
				self.save_fuel_economy(self.imei, time_to_start.date(), final_fuel_economy)

			if fuel_emission_list:
				self.save_fuel_emission(self.imei, time_to_start.date(), fuel_emission_list)

			if fuel_emission_list:
				self.save_fuel_consumption(self.imei, time_to_start.date(), fuel_emission_list)

		return final_fuel_economy

	def save_fuel_economy(self, imei, date, fuel_economy):
		if fuel_economy:
			if fuel_economy>0:
				fuel_event = FuelEconomy.objects.filter(imei=imei, record_date=date).all()
				if fuel_event:
					fuel_event.delete()

				voltage_obj = {
					'imei': imei,
					'fuel_economy': fuel_economy,
					'record_date':date,
					'customer_id':self.customer_id
				}
				serializer = FuelEconomySerializer(data=voltage_obj)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
		pass


	def save_fuel_consumption(self, imei, date, fuel_economy):
		if fuel_economy:
			if fuel_economy>0:
				fuel_event = FuelConsumption.objects.filter(imei=imei, record_date=date).all()
				if fuel_event:
					fuel_event.delete()
					

				fuel_consumption_obj = {
					'imei':imei,
					'consumption':sum(fuel_economy),
					'record_date': date,
					'customer_id':self.customer_id
				}
				serializer = FuelConsumptionSerializer(data=fuel_consumption_obj)
				if serializer.is_valid():
					serializer.save()
		pass


	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			self.customer_id = sub.customer_id
			try:
				user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
				if user:
					return user.time_zone
			except(Exception)as e:
				print(e)
				return None
		return None


	def save_fuel_emission(self, imei, date, emission):
		if emission:
			if emission>0:
				emission_obj = Emission.objects.filter(imei=imei, record_date=date).all()
				if emission_obj:
					emission_obj.delete()

				economy = sum(emission)*8.8
				voltage_obj = {
					'imei': imei,
					'emission': economy,
					'record_date':date,
					'customer_id':self.customer_id
				}
				serializer = EmissionSerializer(data=voltage_obj)
				if serializer.is_valid():
					serializer.save()
					close_old_connections()
		pass


	def get_data(self, imei, time_date_start, time_date_end):
		try:
			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()
		except(Exception)as e:
			send_time_start = int(time_date_start.strftime("%Y%m%d%H%M%S"))
			send_time_end = int(time_date_end.strftime("%Y%m%d%H%M%S"))
			stt = EngineSummary.objects.filter(imei=imei, send_time__gte=send_time_start, send_time__lte=send_time_end).all()

		stt_serializer = EngineSummarySerializer(stt, many=True).data
		data = [dict(i) for i in stt_serializer]
		records = sorted(data, key = lambda i: i['send_time'],reverse=False)
		return records

	def get_fuel_capacity(self, imei):
		fuel = SettingsModel.objects.filter(imei=imei).last()
		if fuel:
			if fuel.fuel_capacity:
				return fuel.fuel_capacity
			return None
		return None


	def get_date_to_filter(self, timezone, day, month, year):
		timestamp = datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 00:00:00', date_time_fmt)
		old_timezone = pytz.timezone(timezone)

		new_timezone = pytz.timezone("UTC")
		my_timestamp_in_new_timezone = old_timezone.localize(timestamp).astimezone(new_timezone)
		timestamp_end = datetime.strptime(str(year)+'-'+str(month)+'-'+str(day)+' 23:59:59', date_time_fmt)
		old_timezone_end = pytz.timezone(timezone)
		new_timezone_end = pytz.timezone("UTC")
		my_timestamp_in_new_timezone_end = old_timezone_end.localize(timestamp_end).astimezone(new_timezone_end)
		return my_timestamp_in_new_timezone, my_timestamp_in_new_timezone_end







class EmissionMachine:
	def __init__(self, trip_id):
		self.trip_id = trip_id
		self.imei = None

	def receive_trip_event(self):
		try:
			trip = UserObdTrip.objects.filter(id=self.trip_id).first()
		except(Exception)as e:
			trip = None
		self.imei = trip.imei

		if trip and self.trip_id:
			try:
				trip_logs = trip.trip_log
			except(Exception)as e:
				trip_logs = None

			try:
				fuel_event = Emission.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)

			start_trip_log = trip_logs[0]
			end_trip_log = trip_logs[-1]

			if start_trip_log[0].get('fuel_consumption'):
				start_fuel = start_trip_log[0].get('fuel_consumption')
			else:
				start_fuel = start_trip_log[1].get('fuel_consumption')


			if end_trip_log[-1].get('fuel_consumption'):
				end_fuel = end_trip_log[-1].get('fuel_consumption')
			else:
				end_fuel = end_trip_log[-2].get('fuel_consumption')

			try:
				fuel_consumed = float(end_fuel) - float(start_fuel)
			except(Exception)as e:
				fuel_consumed = 0

			try:
				fuel_consumed_save = float(end_fuel) - float(start_fuel)
			except(Exception)as e:
				fuel_consumed_save = 0

			try:
				fuel_consumed = fuel_consumed/3785.412
			except(Exception)as e:
				fuel_consumed = fuel_consumed

			try:
				economy = fuel_consumed*8.8
			except(Exception)as e:
				economy = 0

			customer_id = self.get_customer_id(self.imei)
			voltage_obj = {
				'imei': self.imei,
				'emission': economy,
				'record_date':trip.record_date_timezone.date(),
				'customer_id':customer_id
			}
			# print(voltage_obj)
			try:
				fuel_event = Emission.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)

			serializer = EmissionSerializer(data=voltage_obj)
			if serializer.is_valid():
				serializer.save()
				close_old_connections()


			try:
				fuel_event = FuelConsumption.objects.filter(imei=self.imei, record_date=trip.record_date_timezone.date()).all()
				if fuel_event:
					fuel_event.delete()
			except(Exception)as e:
				print(e)

			fuel_consumption_obj = {
				'imei':self.imei,
				'consumption':fuel_consumed,
				'record_date': trip.record_date_timezone.date(),
				'customer_id':customer_id
			}
			serializer = FuelConsumptionSerializer(data=fuel_consumption_obj)
			if serializer.is_valid():
				serializer.save()
			else:
				pass
		pass


	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None

	def format_date(self, date):
		date_time = datetime.datetime.strptime(date[:4]+'-'+date[4:6]+'-'+date[6:8]+' '+date[-6:-4]+':'+date[-4:-2]+':'+date[-2:], date_time_fmt)
		time_zone = self.get_time_zone(self.imei)
		date_time = date_time.astimezone(pytz.timezone(time_zone))
		return date_time

	def get_time_zone(self, imei):
		sub = Subscription.objects.filter(imei_no=imei).last()
		if sub:
			user = User.objects.filter(customer_id=sub.customer_id, subuser=False).first()
			close_old_connections()
			if user:
				return user.time_zone
		close_old_connections()
		return 'UTC'

	def get_customer_id(self, imei):
		customer_id = Subscription.objects.filter(imei_no=imei).last()
		close_old_connections()
		if customer_id:
			return customer_id.customer_id
		return None


