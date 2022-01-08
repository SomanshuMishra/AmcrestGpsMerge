from django_cron import CronJobBase, Schedule
import json
from datetime import datetime, timedelta
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

from services.models import *
from services.serializers import *

from app.events.trips import trip_event_module

from services.mail_sender import *

User = get_user_model()

time_fmt = '%Y-%m-%d %H:%M:%S'

UTC=pytz.UTC

class ReviewCronMachine(CronJobBase):
	RUN_EVERY_MINS = 0
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'app.cron.review_cron'

	def do(self):
		last_month = datetime.datetime.now() - timedelta(days=60)
		last_month_1 = datetime.datetime.now() - timedelta(days=61)
		users = User.objects.filter(date_joined__lte=last_month.date(), date_joined__gte=last_month_1.date(), is_dealer=False, is_dealer_user=False, is_active=True, subuser=False).all()
		
		try:
			for user in users:
				self.check_subscriptions(user)
		except(Exception)as e:
			print(e)

	def check_subscriptions(self, user):
		subs = Subscription.objects.filter(is_active=True, device_in_use=True, device_listing=True, customer_id=user.customer_id).all()
		if subs:
			today = datetime.datetime.now()
			last_month = datetime.datetime.now() - timedelta(days=60)
			for sub in subs:
				try:
					customer_id = str(sub.customer_id)
				except(Exception)as e:
					customer_id = None

				user_trip = UserTrip.objects.filter(imei=sub.imei_no, customer_id=customer_id, record_date_timezone__lte=today, record_date_timezone__gte=last_month).all()
				try:
					if len(user_trip) >= 20:
						self.send_review_mail(user.emailing_address, user.customer_id, user.first_name, user.last_name)
						break
					else:
						user_trip = UserObdTrip.objects.filter(imei=sub.imei_no, customer_id=customer_id, record_date_timezone__lte=today, record_date_timezone__gte=last_month).all()
						if len(user_trip) >= 20:
							self.send_review_mail(user.emailing_address, user.customer_id, user.first_name, user.last_name)
							break
						pass
				except(Exception)as e:
					print(e)


	def send_review_mail(self, email, customer_id, first_name, last_name):
		last_month = datetime.datetime.now() - timedelta(days=60)
		is_sent = ReviewModel.objects.filter(customer_id=customer_id, email=email).last()
		if is_sent:
			# print(is_sent.record_date>UTC.localize(last_month), is_sent.record_date, last_month)
			# if not is_sent.record_date>UTC.localize(last_month):
			# 	review_mail([email, customer_id, first_name, last_name])
			# 	self.save_review_message_alert(email, customer_id)
			# 	print('sent')
			# 	pass
			# else:
			# 	pass
			pass
		else:
			review_mail([email, customer_id])
			self.save_review_message_alert(email, customer_id)
			pass


	def save_review_message_alert(self, email, customer_id):
		serializer = ReviewModelSerializer(data={
				'email':email,
				'customer_id':customer_id
			})
		if serializer.is_valid():
			serializer.save()
		else:
			print(serializer.errors)






class ReviewBulkCronMachine(CronJobBase):
	RUN_EVERY_MINS = 0
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'app.cron.review_cron'

	def do(self):
		last_month = datetime.datetime.now() - timedelta(days=60)
		registered_date = datetime.datetime.now() - timedelta(days=500)
		is_sent = ReviewModel.objects.all().distinct().values('customer_id')
		try:
			users = User.objects.filter(date_joined__gte=registered_date.date(), date_joined__lte=last_month.date(), is_dealer=False, is_dealer_user=False, is_active=True, subuser=False).exclude(customer_id__in=is_sent).all()[:20]
		except(Exception)as e:
			print(e)
		
		try:
			for user in users:
				self.check_subscriptions(user)
		except(Exception)as e:
			print(e)

	def check_subscriptions(self, user):
		subs = Subscription.objects.filter(is_active=True, device_in_use=True, device_listing=True, customer_id=user.customer_id).all()
		if subs:
			today = datetime.datetime.now()
			last_month = datetime.datetime.now() - timedelta(days=60)
			for sub in subs:
				try:
					customer_id = str(sub.customer_id)
				except(Exception)as e:
					customer_id = None

				user_trip = UserTrip.objects.filter(imei=sub.imei_no, customer_id=customer_id, record_date_timezone__lte=today, record_date_timezone__gte=last_month).all()
				try:
					if len(user_trip) >= 20:
						self.send_review_mail(user.emailing_address, user.customer_id, user.first_name, user.last_name)
						break
					else:
						user_trip = UserObdTrip.objects.filter(imei=sub.imei_no, customer_id=customer_id, record_date_timezone__lte=today, record_date_timezone__gte=last_month).all()
						if len(user_trip) >= 20:
							self.send_review_mail(user.emailing_address, user.customer_id, user.first_name, user.last_name)
							break
						pass
				except(Exception)as e:
					print(e)


	def send_review_mail(self, email, customer_id, first_name, last_name):
		last_month = datetime.datetime.now() - timedelta(days=60)
		is_sent = ReviewModel.objects.filter(customer_id=customer_id, email=email).last()
		if is_sent:
			# print(is_sent.record_date>UTC.localize(last_month), is_sent.record_date, last_month)
			# if not is_sent.record_date>UTC.localize(last_month):
			# 	review_mail([email, customer_id, first_name, last_name])
			# 	self.save_review_message_alert(email, customer_id)
			# 	print('sent')
			# 	pass
			# else:
			# 	pass
			pass
		else:
			review_mail([email, customer_id])
			self.save_review_message_alert(email, customer_id)
			pass


	def save_review_message_alert(self, email, customer_id):
		serializer = ReviewModelSerializer(data={
				'email':email,
				'customer_id':customer_id
			})
		if serializer.is_valid():
			serializer.save()
		else:
			print(serializer.errors)



# No review mail to dealer
