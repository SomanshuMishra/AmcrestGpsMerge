from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.db import close_old_connections

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import string
import random
import datetime
from datetime import datetime, timedelta
import time
import datedelta

from .serializers import *
from .models import *

from listener.models import *
from listener.serializers import *

from app.location_finder import *

from app.cron import buffer_trip_cron

import mongoengine
import urllib.parse

time_fmt = '%Y-%m-%d %H:%M:%S'

class GetAvailableDates(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.running_from = None
		self.send_time = None
		
	def getold(self, request, customer_id, imei):
		close_old_connections()
		# mongoengine.connect(host="mongodb+srv://"+urllib.parse.quote_plus(settings.MONGO_USER)+":"+urllib.parse.quote_plus(settings.MONGO_PASSWORD)+"@amcrestobd-hhn08.mongodb.net/test?retryWrites=true", alias='available_trip_dates')
		category = request.GET.get('category', None)
		if category == 'gps':
			check_trip_running = self.get_current_trip_data(imei)
		else:
			check_trip_running = self.get_current_obd_trip_data(imei)

		check_imei = Subscription.objects.filter(imei_no=imei, customer_id=customer_id).last()
		if check_imei:
			time_threshold = datetime.datetime.now() - datedelta.datedelta(months=6)
			from_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 00:00:00'
			
			if category == 'obd':
				user_trip = UserObdTrip.objects.filter(imei=imei, customer_id=customer_id, record_date__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all().order_by('-record_date')
				
				serializer = TripObdDateAvailableSerializer(user_trip, many=True)
			else:
				user_trip = UserTrip.objects.filter(imei=imei, customer_id=customer_id, record_date__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all().order_by('-record_date')

				serializer = TripDateAvailableSerializer(user_trip, many=True)
			# disconnect(alias='available_trip_dates')
			return JsonResponse({'message': 'Avalailable Trip Dates', 'status_code':200, 'status':True, 'details':serializer.data, 'trip_running':check_trip_running, 'running_from':self.running_from, 'trip_start_time':self.send_time}, status=200)
		else:
			# disconnect(alias='available_trip_dates')
			return JsonResponse({'message': 'No Trips Avalailable', 'status_code':200, 'status':True, 'details':[], 'trip_running':check_trip_running, 'running_from':self.running_from, 'trip_start_time':self.send_time}, status=200)

	def get(self, request, customer_id, imei):
		close_old_connections()
		print(('HEERE'))

		# category = request.GET.get('category', None)
		gps_check_trip_running = self.get_current_trip_data(imei)
		print(('HEERE1'))

		obd_check_trip_running = self.get_current_obd_trip_data(imei)
		print(('HEERE2'))

		check_imei = Subscription.objects.filter(imei_no=imei, customer_id=customer_id).last()
		if check_imei:
			time_threshold = datetime.datetime.now() - datedelta.datedelta(months=6)
			from_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 00:00:00'
			print('HERE3')
			obd_user_trip = UserObdTrip.objects.filter(imei=imei, customer_id=customer_id, record_date__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all().order_by('-record_date')
			print('CHECK')
			obd_serializer = TripObdDateAvailableSerializer(obd_user_trip, many=True)
			
			gps_user_trip = UserTrip.objects.filter(imei=imei, customer_id=customer_id, gps_record_date__gte=datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')).all().order_by('-record_date')
			gps_serializer = TripDateAvailableSerializer(user_trip, many=True)
			
			return JsonResponse({'message': 'Avalailable Trip Dates', 'status_code':200, 'status':True, 'obd':{'obd_details':obd_serializer.data, 'obd_trip_running':obd_check_trip_running, 'running_from':self.running_from, 'trip_start_time':self.send_time},'gps':{'gps_details':gps_serializer.data, 'gps_trip_running':gps_check_trip_running, 'running_from':self.running_from, 'trip_start_time':self.send_time}}, status=200)
		else:
			# disconnect(alias='available_trip_dates')
			return JsonResponse({'message': 'No Trips Avalailable', 'status_code':200, 'status':True, 'details':[], 'trip_running':check_trip_running, 'running_from':self.running_from, 'trip_start_time':self.send_time}, status=200)


	def get_current_trip_data(self, imei):
		import datetime
		stt_marker = SttMarkers.objects.filter(imei=imei, report_name='+RESP:GTSTT').last()
		if stt_marker:
			if stt_marker.state == 42:
				gl_marker = GLFriMarkers.objects.filter(imei=imei).last()
				if gl_marker:
					time_diff = (
						time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
		                time.mktime(time.strptime(datetime.datetime.strftime(gl_marker.record_date, time_fmt), time_fmt))
		                )
					if((time_diff/60)<1):
						self.running_from = get_location(str(stt_marker.longitude), str(stt_marker.latitude))
						self.send_time = stt_marker.send_time
						return True
				else:
					time_diff = (
						time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
		                time.mktime(time.strptime(datetime.datetime.strftime(stt_marker.record_date, time_fmt), time_fmt))
		                )
					if((time_diff/60)<1):
						self.running_from = get_location(str(stt_marker.longitude), str(stt_marker.latitude))
						self.send_time = stt_marker.send_time
						return True
				return False
			return False
		return False

	def get_current_obd_trip_data(self, imei):
		import datetime
		last_obd = ObdMarkers.objects.filter(imei=imei).last()

		if last_obd:
			if last_obd.device_status == 'engine_start':
				time_diff = (
					time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
					time.mktime(time.strptime(datetime.datetime.strftime(last_obd.record_date, time_fmt), time_fmt))
					)

				if((time_diff/60)<2):
					self.running_from = get_location(str(last_obd.longitude), str(last_obd.latitude))
					self.send_time = stt_marker.send_time
					return True
				return False
			return False
		return False




class GetTripListView(APIView):
	# permission_classes = (AllowAny,)
	def __init__(self):
		self.running_from = None
		self.send_time = None
		
	def get(self, request, customer_id, imei, date, month, year):
		close_old_connections()
		trip_mesurement = None
		try:
			customer_id = request.user.customer_id
		except Exception as e:
			customer_id = None

		category = request.GET.get('category', None)

		if customer_id:
			check_imei = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()
			if check_imei:
				record_date_gte = datetime.datetime.strptime(year+"-"+month+"-"+date+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(year+"-"+month+"-"+date+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				
				if category == 'obd':
					user_trip = UserObdTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=str(customer_id)).first()
					serializer = UserObdTripSerializer(user_trip)
				else:
					user_trip = UserTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=str(customer_id)).first()
					serializer = UserTripSerializer(user_trip)

				if user_trip:
					if category == 'obd':
						trip_mesurement = TripsObdMesurement.objects.filter(measure_id=user_trip.measure_id).first()
						m_serializer = TripsObdMesurementSerializer(trip_mesurement)
						trip_mesurement = m_serializer.data
					else:
						trip_mesurement = TripsMesurement.objects.filter(measure_id=user_trip.measure_id).first()
						m_serializer = TripsMesurementSerializer(trip_mesurement)
						trip_mesurement = m_serializer.data

					if category == 'gps':
						check_trip_running = self.get_current_trip_data(imei)
					else:
						check_trip_running = self.get_current_obd_trip_data(imei)

					idle_time_records = []
					_date = {
						'start':user_trip.trip_log[0][0].get('send_time'),
						'end':serializer.data['trip_log'][-1][-1].get('send_time')
					}
					idle_time = self.idle_time(_date, imei)
					idle_time_records = self.get_idle_time_records(_date, imei)


					return JsonResponse({'message':'Trip List For date : '+date+'-'+month+'-'+year, 'status_code':200, 'status':True, 'imei':imei, 'trip_log':serializer.data, 'trip_running':check_trip_running, 'trip_measurement':m_serializer.data, 'running_from':self.running_from, 'idle_records':idle_time_records, 'idle_time':idle_time, 'trip_start_time':self.send_time}, status=200)
				return JsonResponse({'message':'Trip not found', 'imei':imei, 'trip_log':[], 'status':False, 'status_code':200, 'idle_records': [], 'idle_time': 0, 'trip_running': False, 'trip_measurement': {}, 'running_from':None, 'trip_start_time':self.send_time}, status=200)
			else:
				return JsonResponse({'message':'Invalid IMEI, Please check IMEI', 'imei':imei, 'trip_log':[], 'status':False, 'status_code':200, 'idle_records': [], 'idle_time': 0, 'trip_running': False, 'trip_measurement': {}, 'running_from':None, 'trip_start_time':self.send_time}, status=200)
		else:
			return JsonResponse({'message':'Error During Getting Record', 'status':False, 'status_code':400}, status=200)

	def get_current_obd_trip_data(self, imei):
		import datetime
		
		last_obd = ObdMarkers.objects.filter(imei=imei).last()

		if last_obd:
			if last_obd.device_status == 'engine_start':
				time_diff = (
					time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
					time.mktime(time.strptime(datetime.datetime.strftime(last_obd.record_date, time_fmt), time_fmt))
					)

				if((time_diff/60)<2):
					self.running_from = get_location(str(last_obd.longitude), str(last_obd.latitude))
					self.send_time = last_obd.send_time
					return True
				return False
			return False
		return False


	def get_idle_time_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

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

	def get_current_trip_data(self, imei):
		import datetime
		stt_marker = SttMarkers.objects.filter(imei=imei, report_name='+RESP:GTSTT').last()
		if stt_marker:
			if stt_marker.state == 42:
				gl_marker = GLFriMarkers.objects.filter(imei=imei).last()
				if gl_marker:
					time_diff = (
						time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
		                time.mktime(time.strptime(datetime.datetime.strftime(gl_marker.record_date, time_fmt), time_fmt))
		                )
					if((time_diff/60)<1):
						self.running_from = get_location(str(stt_marker.longitude), str(stt_marker.latitude))
						self.send_time = stt_marker.send_time
						return True
				else:
					time_diff = (
						time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
		                time.mktime(time.strptime(datetime.datetime.strftime(stt_marker.record_date, time_fmt), time_fmt))
		                )
					if((time_diff/60)<1):
						self.running_from = get_location(str(stt_marker.longitude), str(stt_marker.latitude))
						self.send_time = stt_marker.send_time
						return True
				return False
			return False
		return False


	def delete(self, request, customer_id, imei, date, month, year):
		close_old_connections()
		try:
			customer_id = request.user.customer_id
		except Exception as e:
			customer_id = None

		category = request.GET.get('category', 'gps')

		if customer_id:
			check_imei = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()
			if check_imei:
				record_date_gte = datetime.datetime.strptime(year+"-"+month+"-"+date+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(year+"-"+month+"-"+date+" 23:59:59", "%Y-%m-%d %H:%M:%S")

				if category == 'gps':
					user_trip = UserTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
					user_trip.delete()
				else:
					user_trip = UserObdTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
					user_trip.delete()
				close_old_connections()
				return JsonResponse({'message':'Deleted Trips For date : '+date+'-'+month+'-'+year, 'status_code':200, 'status':True, 'imei':imei}, status=200)
			else:
				return JsonResponse({'message':'Invalid IMEI, Please check IMEI', 'imei':imei, 'status':False, 'status_code':200}, status=200)
		else:
			return JsonResponse({'message':'Error During Getting Record', 'status':False, 'status_code':400}, status=200)





class TripMesurementView(APIView):
	def get(self, request, measure_id):
		close_old_connections()
		try:
			customer_id = request.user.customer_id
		except(Exception)as e:
			customer_id = None

		category = request.GET.get('category', 'gps')

		if customer_id:
			if category == 'gps':
				trips_mesurement = TripsMesurement.objects.filter(measure_id=measure_id).first()
			else:
				trips_mesurement = TripsObdMesurement.objects.filter(measure_id=measure_id).first()

			if trips_mesurement:
				serializer = TripsMesurementSerializer(trips_mesurement)
				return JsonResponse({'message':'Measurement For Trip', 'status_code':200, 'status':True, 'trip_mesurement':serializer.data}, status=200)
			return JsonResponse({'message':'Invalid Measure ID', 'status':False, 'status_code':404}, status=404)
		return JsonResponse({'message':'Error During Getting Record', 'status':False, 'status_code':400}, status=200)


class CurrentTripView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei):
		close_old_connections()
		type_ = request.GET.get('category', None)
		if type_ == 'gps':
			stt = SttMarkers.objects.filter(imei=imei).last()
			if stt:
				stt_serializer = SttMarkersSerializer(stt)
				fri = GLFriMarkers.objects.filter(mileage__gte=stt.mileage, imei=imei, send_time__gte=stt.send_time).all()
				serializer = GLFriMarkersSerializer(fri, many=True)
				data_to_send = [stt_serializer.data]+serializer.data
				data_to_send = sorted(data_to_send, key = lambda i: i['send_time'],reverse=False)
			else:
				data_to_send = []
			return JsonResponse({'message':'Current Trip', 'status':True, 'status_code':200, 'trip':data_to_send}, status=200)
		else:
			ign = IgnitionOnoff.objects.filter(imei=imei, protocol='+RESP:GTIGN').last()
			if ign:
				ign_serializer = IgnitionOnoffSerializer(ign)
				obd = ObdMarkers.objects.filter(mileage__gte=ign.mileage, imei=imei, send_time__gte=ign.send_time).all()
				serializer = ObdMarkersSerializer(obd, many=True)
				data_to_send = [ign_serializer.data]+serializer.data
				data_to_send = sorted(data_to_send, key = lambda i: i['send_time'],reverse=False)
			else:
				data_to_send = []
			return JsonResponse({'message':'Current Trip', 'status':True, 'status_code':200, 'trip':data_to_send}, status=200)
		return JsonResponse({'message':'Currently trip not in progress', 'status':False, 'status_code':200}, status=200)


class LastTripView(APIView):
	# permission_classes = (AllowAny,)
	def getold(self, request, imei, customer_id):
		type_ = request.GET.get('category', 'gps')
		if type_ == 'gps':
			user_trip = UserTrip.objects.filter(imei=imei, customer_id=customer_id).order_by('-id').first()
		else:
			user_trip = UserObdTrip.objects.filter(imei=imei, customer_id=customer_id).order_by('-id').first()

		idle_time_records = []
		idle_times = 0
		if user_trip:
			trip_measurement = self.get_trip_measurements(user_trip.measure_id, type_)
			trip_object = {}
			trip_object['last_trip'] = user_trip.trip_log[-1]
			trip_object['distance'] = trip_measurement['total_distance'][-1]
			trip_object['time'] = trip_measurement['total_time'][-1]
			if request.GET.get('category') == 'obd':
				
				date = {
					'start':user_trip.trip_log[0][0].get('send_time'),
					'end':user_trip.trip_log[-1][-1].get('send_time')
				}
				idle_times = self.idle_time(date, imei)
				idle_time_records = self.get_idle_time_records(date, imei)
			return JsonResponse({'message':'Last Trip Log', 'status':True, 'status_code':200, 'trip':trip_object, 'idle_records':idle_time_records, 'idle_time':idle_times}, status=200)
		return JsonResponse({'message':'Invalid Details, cannot find trip', 'status':False, 'status_code':404}, status=200)


	def get(self, request, imei, customer_id):
		gps_user_trip = UserTrip.objects.filter(imei=imei, customer_id=customer_id).order_by('-id').first()
		obd_user_trip = UserObdTrip.objects.filter(imei=imei, customer_id=customer_id).order_by('-id').first()
		if gps_user_trip & obd_user_trip:
			# For GPS Last Trip
			gps_idle_time_records = []
			gps_idle_times = 0
			type_='gps'
			gps_trip_measurement = self.get_trip_measurements(gps_user_trip.measure_id, type_)
			gps_trip_object = {}
			gps_trip_object['last_trip'] = gps_user_trip.trip_log[-1]
			gps_trip_object['distance'] = trip_measurement['total_distance'][-1]
			gps_trip_object['time'] = trip_measurement['total_time'][-1]
			# For OBD Last Trip
			type_='obd'
			obd_trip_measurement = self.get_trip_measurements(obd_user_trip.measure_id, type_)
			obd_trip_object = {}
			obd_trip_object['last_trip'] = user_trip.trip_log[-1]
			obd_trip_object['distance'] = trip_measurement['total_distance'][-1]
			obd_trip_object['time'] = trip_measurement['total_time'][-1]
			date = {
					'start':user_trip.trip_log[0][0].get('send_time'),
					'end':user_trip.trip_log[-1][-1].get('send_time')
				}
			obd_idle_times = self.idle_time(date, imei)
			obd_idle_time_records = self.get_idle_time_records(date, imei)

			return JsonResponse({'message':'Last Trip Log of GPS and OBD', 'status':True, 'status_code':200 , 'gps':{ 'gps_trip':gps_trip_object, 'gps_idle_time_records':gps_idle_time_records, 'gps_idle_times':gps_idle_times}, 'obd':{ 'obd_trip':obd_trip_object, 'obd_idle_time_records':obd_idle_time_records, 'obd_idle_times':obd_idle_times}}, status=200)

		elif gps_user_trip:
			type_='gps'
			trip_measurement = self.get_trip_measurements(user_trip.measure_id, type_)
			trip_object = {}
			trip_object['last_trip'] = user_trip.trip_log[-1]
			trip_object['distance'] = trip_measurement['total_distance'][-1]
			trip_object['time'] = trip_measurement['total_time'][-1]
			return JsonResponse({'message':'Last Trip Log', 'status':True, 'status_code':200, 'gps_trip':trip_object, 'gps_idle_records':idle_time_records, 'gps_idle_time':idle_times}, status=200)

		elif obd_user_trip:
			type_='obd'
			obd_trip_measurement = self.get_trip_measurements(obd_user_trip.measure_id, type_)
			obd_trip_object = {}
			obd_trip_object['last_trip'] = user_trip.trip_log[-1]
			obd_trip_object['distance'] = trip_measurement['total_distance'][-1]
			obd_trip_object['time'] = trip_measurement['total_time'][-1]
			date = {
					'start':user_trip.trip_log[0][0].get('send_time'),
					'end':user_trip.trip_log[-1][-1].get('send_time')
				}
			obd_idle_times = self.idle_time(date, imei)
			obd_idle_time_records = self.get_idle_time_records(date, imei)
			return JsonResponse({'message':'Last Trip Log', 'status':True, 'status_code':200, 'obd_trip':obd_trip_object, 'obd_idle_records':obd_idle_time_records, 'obd_idle_time':obd_idle_times}, status=200)
  
		return JsonResponse({'message':'Invalid Details, cannot find trip', 'status':False, 'status_code':404}, status=200)

	def get_trip_measurements(self, measure_id, type_):
		if type_ == 'gps':
			trip_measure = TripsMesurement.objects.filter(measure_id=measure_id).first()
			serializer = TripsMesurementSerializer(trip_measure, many=False)
		else:
			trip_measure = TripsObdMesurement.objects.filter(measure_id=measure_id).first()
			serializer = TripsObdMesurementSerializer(trip_measure, many=False)

		return serializer.data

	def get_idle_time_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

	def idle_time(self, date, imei):
		total_time = 0
		start_idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), protocol='+RESP:GTIDN', imei=imei).all()
		end_idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), protocol='+RESP:GTIDF', imei=imei).all()
		
		
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


class TripsRangeView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei):
		close_old_connections()
		idle_time_records = []
		idle_time = 0
		# try:
		# 	customer_id = request.user.customer_id
		# except(Exception)as e:
		# 	customer_id = None
		# customer_id = 268102
		range_from = request.GET.get('from')
		range_to = request.GET.get('to')

		type_ = request.GET.get('category', 'gps')

		if customer_id:
			if range_from and range_to:
				check_imei = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()
				if check_imei:
					record_date_gte = datetime.datetime.strptime(range_from.strip()+" 00:00:00", "%Y-%m-%d %H:%M:%S")
					record_date_lte = datetime.datetime.strptime(range_to.strip()+" 23:59:59", "%Y-%m-%d %H:%M:%S")
					
					if type_ == 'gps':
						user_trip = UserTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).order_by('record_date').all()
						serializer = UserTripSerializer(user_trip, many=True)
					else:
						user_trip = UserObdTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).order_by('record_date').all()
						serializer = UserObdTripSerializer(user_trip, many=True)

					measure_id = [ut.get('measure_id') for ut in serializer.data]
					trip_measurement = self.get_trip_measurements(measure_id, type_)

					idle_time_records = []
					if user_trip:
						date = {
							'start':user_trip[0].trip_log[0][0].get('send_time'),
							'end':serializer.data[-1]['trip_log'][-1][-1].get('send_time')
						}
						idle_time = self.idle_time(date, imei)
						idle_time_records = self.get_idle_time_records(date, imei)

					return JsonResponse({'message':'List Of Trips From date : '+range_from+', To Date : '+range_to, 'status_code':200, 'status':True, 'imei':imei, 'trips':serializer.data, 'trip_measurement':trip_measurement, 'idle_records':idle_time_records, 'idle_time':idle_time}, status=200)
				else:
					return JsonResponse({'message':'Invalid IMEI, Please check IMEI', 'imei':imei, 'trips':[], 'status':False, 'status_code':400}, status=200)
			else:
				return JsonResponse({'message':'Please Provide "From Date" and "To Date"', 'imei':imei, 'status':False, 'status_code':200}, status=200)
		else:
			return JsonResponse({'message':'Error During Getting Record', 'status':False, 'status_code':400}, status=200)


	def get_trip_measurements(self, measure_id, type_):
		if type_ == 'gps':
			trip_measure = TripsMesurement.objects.filter(measure_id__in=measure_id).all()
			serializer = TripsMesurementSerializer(trip_measure, many=True)
		else:
			trip_measure = TripsObdMesurement.objects.filter(measure_id__in=measure_id).all()
			serializer = TripsObdMesurementSerializer(trip_measure, many=True)

		trip_mesure = []
		# print(measure_id)
		for i in measure_id:
			for j in serializer.data:
				# print(j['measure_id'])
				if str(j['measure_id']) == str(i):
					trip_mesure.append(j)
		return trip_mesure


	def get_idle_time_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

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

class LastSevenDayTripView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei, customer_id):
		if imei and customer_id:
			idle_time = 0
			idle_time_records = []
			today = datetime.datetime.now()
			last_date = today - datetime.timedelta(days = 7)

			type_ = request.GET.get('category', 'gps')

			record_date_gte = datetime.datetime.strptime(str(last_date.year)+'-'+str(last_date.month)+'-'+str(last_date.day)+" 00:00:00", "%Y-%m-%d %H:%M:%S")
			record_date_lte = datetime.datetime.strptime(str(today.year)+'-'+str(today.month)+'-'+str(today.day)+" 23:59:59", "%Y-%m-%d %H:%M:%S")

			check_imei = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()
			if check_imei:

				if type_ == 'gps':
					user_trip = UserTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
				else:
					user_trip = UserObdTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()


				measure_id = [ut.measure_id for ut in user_trip]
				trip_measurement = self.get_trip_measurements(measure_id, type_)

				if type_ == 'gps':
					serializer = UserTripSerializer(user_trip, many=True)
				else:
					serializer = UserObdTripSerializer(user_trip, many=True)

				if user_trip:
					idle_time_records = []
					date = {
						'start':user_trip[0].trip_log[0][0].get('send_time'),
						'end':serializer.data[-1]['trip_log'][-1][-1].get('send_time')
					}
					idle_time = self.idle_time(date, imei)
					idle_time_records = self.get_idle_time_records(date, imei)

				return JsonResponse({'message':'List Of Last 7 days Trips ', 'status_code':200, 'status':True, 'imei':imei, 'trips':serializer.data, 'trip_measurement':trip_measurement, 'idle_records':idle_time_records, 'idle_time':idle_time}, status=200)
			return JsonResponse({'message':'Invalid IMEI, Please check IMEI', 'imei':imei, 'trips':[], 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'IMEI and Customer ID required', 'status':False, 'status_code':400}, status=200)


	def get_trip_measurements(self, measure_id, type_):
		if type_ == 'gps':
			trip_measure = TripsMesurement.objects.filter(measure_id__in=measure_id).all()
			serializer = TripsMesurementSerializer(trip_measure, many=True)
		else:
			trip_measure = TripsObdMesurement.objects.filter(measure_id__in=measure_id).all()
			serializer = TripsObdMesurementSerializer(trip_measure, many=True)
		return serializer.data

	def get_engine_summary_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

	def get_idle_time_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

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


class LastThirtyDayTripView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, imei, customer_id):
		type_ = request.GET.get('category', 'gps')

		if imei and customer_id:
			today = datetime.datetime.now()
			last_date = today - datetime.timedelta(days = 30)
			record_date_gte = datetime.datetime.strptime(str(last_date.year)+'-'+str(last_date.month)+'-'+str(last_date.day)+" 00:00:00", "%Y-%m-%d %H:%M:%S")
			record_date_lte = datetime.datetime.strptime(str(today.year)+'-'+str(today.month)+'-'+str(today.day)+" 00:00:00", "%Y-%m-%d %H:%M:%S")
			idle_time_records = []
			check_imei = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()


			if check_imei:
				if type_ == 'gps':
					user_trip = UserTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
					serializer = UserTripSerializer(user_trip, many=True)
				else:
					user_trip = UserObdTrip.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
					serializer = UserObdTripSerializer(user_trip, many=True)

				idle_time_records = []
				idle_time = 0
				if user_trip:
					date = {
						'start':user_trip[0].trip_log[0][0].get('send_time'),
						'end':serializer.data[-1]['trip_log'][-1][-1].get('send_time')
					}
					idle_time = self.idle_time(date, imei)
					idle_time_records = self.get_idle_time_records(date, imei)

				measure_id = [ut.measure_id for ut in user_trip]
				trip_measurement = self.get_trip_measurements(measure_id, type_)
				
				return JsonResponse({'message':'List Of Last 30 days Trips ', 'status_code':200, 'status':True, 'imei':imei, 'trips':serializer.data, 'trip_measurement':trip_measurement, 'idle_records':idle_time_records, 'idle_time':idle_time}, status=200)
			return JsonResponse({'message':'Invalid IMEI, Please check IMEI', 'imei':imei, 'trips':[], 'status':False, 'status_code':400}, status=200)
		return JsonResponse({'message':'IMEI and Customer ID required', 'status':False, 'status_code':400}, status=200)


	def get_trip_measurements(self, measure_id,type_):
		if type_ == 'gps':
			trip_measure = TripsMesurement.objects.filter(measure_id__in=measure_id).all()
			serializer = TripsMesurementSerializer(trip_measure, many=True)
		else:
			trip_measure = TripsObdMesurement.objects.filter(measure_id__in=measure_id).all()
			serializer = TripsObdMesurementSerializer(trip_measure, many=True)

		return serializer.data

	def get_engine_summary_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

	def get_idle_time_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

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



class BufferTripCron(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request):
		gt = GLFriMarkers.objects.filter(imei='123456789012345').last()
		if gt:
			print(datetime.datetime.strftime(datetime.datetime.now(), time_fmt))
			print(datetime.datetime.strftime(gt.record_date, time_fmt))
			time_diff = (
				time.mktime(time.strptime(datetime.datetime.strftime(datetime.datetime.now(), time_fmt), time_fmt))-\
                time.mktime(time.strptime(datetime.datetime.strftime(gt.record_date, time_fmt), time_fmt))
                )
			print(time_diff/60)

		return JsonResponse({'message':'Buffer Trip Cron', 'status':True, 'status_code':200}, status=200)



class TripBackupApiView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei, date, month, year):
		close_old_connections()
		trip_mesurement = None
		
		category = request.GET.get('category', None)

		if customer_id:
			check_imei = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()
			if check_imei:
				record_date_gte = datetime.datetime.strptime(year+"-"+month+"-"+date+" 00:00:00", "%Y-%m-%d %H:%M:%S")
				record_date_lte = datetime.datetime.strptime(year+"-"+month+"-"+date+" 23:59:59", "%Y-%m-%d %H:%M:%S")
				
				if category == 'gps':
					user_trip = UserTripBackup.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=str(customer_id)).first()
					serializer = UserTripBackupSerializer(user_trip)
				else:
					user_trip = UserTripBackup.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei, customer_id=str(customer_id)).first()
					serializer = UserTripBackupSerializer(user_trip)

				if user_trip:
					trip_mesurement = TripsMesurementBackup.objects.filter(measure_id=user_trip.measure_id).first()
					m_serializer = TripsMesurementBackupSerializer(trip_mesurement)
					trip_mesurement = m_serializer.data

					idle_time_records = []
					_date = {
						'start':user_trip.trip_log[0][0].get('send_time'),
						'end':serializer.data['trip_log'][-1][-1].get('send_time')
					}
					idle_time = self.idle_time(_date, imei)
					idle_time_records = self.get_idle_time_records(_date, imei)


					return JsonResponse({'message':'Trip List For date : '+date+'-'+month+'-'+year, 'status_code':200, 'status':True, 'imei':imei, 'trip_log':serializer.data, 'trip_measurement':m_serializer.data, 'idle_records':idle_time_records, 'idle_time':idle_time}, status=200)
				return JsonResponse({'message':'Trip not found', 'imei':imei, 'trip_log':[], 'status':False, 'status_code':200, 'idle_records': [], 'idle_time': 0, 'trip_running': False, 'trip_measurement': {}, 'running_from':None}, status=200)
			else:
				return JsonResponse({'message':'Invalid IMEI, Please check IMEI', 'imei':imei, 'trip_log':[], 'status':False, 'status_code':200, 'idle_records': [], 'idle_time': 0, 'trip_running': False, 'trip_measurement': {}, 'running_from':None}, status=200)
		else:
			return JsonResponse({'message':'Error During Getting Record', 'status':False, 'status_code':400}, status=200)

	def get_idle_time_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

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


class TripBackupAvailableDates(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei):
		close_old_connections()
		# record_date
		check_imei = Subscription.objects.filter(imei_no=imei, customer_id=customer_id).last()
		time_threshold = datetime.datetime.now() - datedelta.datedelta(months=6)
		to_date = str(time_threshold.year)+'-'+str(time_threshold.month)+'-'+str(time_threshold.day)+' 23:59:59'
		if check_imei:
			user_trip = UserTripBackup.objects.filter(imei=imei, customer_id=customer_id, record_date__lte=datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')).all()
			serializer = TripDateAvailableSerializer(user_trip, many=True)
		# 	# disconnect(alias='available_trip_dates')
			return JsonResponse({'message': 'Avalailable Trip Dates', 'status_code':200, 'status':True, 'details':serializer.data}, status=200)
		else:
			# disconnect(alias='available_trip_dates')
			return JsonResponse({'message': 'No Trips Avalailable', 'status_code':200, 'status':True, 'details':[], 'trip_running':check_trip_running, 'running_from':self.running_from}, status=200)
		return JsonResponse({'message': 'No Trips Avalailable', 'status_code':200, 'status':True, 'details':[]}, status=200)



class BackupTripsRangeView(APIView):
	# permission_classes = (AllowAny,)
	def get(self, request, customer_id, imei):
		close_old_connections()
		idle_time_records = []
		idle_time = 0
		
		# customer_id = 268102
		range_from = request.GET.get('from')
		range_to = request.GET.get('to')
		if customer_id:
			if range_from and range_to:
				check_imei = Subscription.objects.filter(customer_id=customer_id, imei_no=imei).last()
				if check_imei:
					record_date_gte = datetime.datetime.strptime(range_from.strip()+" 00:00:00", "%Y-%m-%d %H:%M:%S")
					record_date_lte = datetime.datetime.strptime(range_to.strip()+" 23:59:59", "%Y-%m-%d %H:%M:%S")
					user_trip = UserTripBackup.objects.filter(record_date_timezone__gte=record_date_gte, record_date_timezone__lte=record_date_lte, imei=imei).all()
					measure_id = [ut.measure_id for ut in user_trip]
					trip_measurement = self.get_trip_measurements(measure_id)
					
					serializer = UserTripBackupSerializer(user_trip, many=True)

					idle_time_records = []
					if user_trip:
						date = {
							'start':user_trip[0].trip_log[0][0].get('send_time'),
							'end':serializer.data[-1]['trip_log'][-1][-1].get('send_time')
						}
						idle_time = self.idle_time(date, imei)
						idle_time_records = self.get_idle_time_records(date, imei)

					return JsonResponse({'message':'List Of Trips From date : '+range_from+', To Date : '+range_to, 'status_code':200, 'status':True, 'imei':imei, 'trips':serializer.data, 'trip_measurement':trip_measurement, 'idle_records':idle_time_records, 'idle_time':idle_time}, status=200)
				else:
					return JsonResponse({'message':'Invalid IMEI, Please check IMEI', 'imei':imei, 'trips':[], 'status':False, 'status_code':400}, status=200)
			else:
				return JsonResponse({'message':'Please Provide "From Date" and "To Date"', 'imei':imei, 'status':False, 'status_code':200}, status=200)
		else:
			return JsonResponse({'message':'Error During Getting Record', 'status':False, 'status_code':400}, status=200)


	def get_trip_measurements(self, measure_id):
		trip_measure = TripsMesurementBackup.objects.filter(measure_id__in=measure_id).all()
		serializer = TripsMesurementBackupSerializer(trip_measure, many=True)
		return serializer.data


	def get_idle_time_records(self, date, imei):
		idle_records = IdleDevice.objects.filter(send_time__lte=date.get('end', None), send_time__gte=date.get('start', None), imei=imei).all()
		serializer = IdleDeviceSerializer(idle_records, many=True)
		return serializer.data

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