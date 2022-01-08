from rest_framework import serializers
# from django.contrib.auth.models import User
from user.models import *
from django.conf import settings
from django.db.models import Sum

from app.models import *
from app.serializers import *
from services.models import *
from listener.models import *
from support.models import *
from user.models import *

# User = get_user_model()



class CreditCardSerializer(serializers.ModelSerializer):
	class Meta:
		model = CreditCardDetails
		fields = '__all__'

class SupportUserSerializer(serializers.ModelSerializer):
	subscriptions = serializers.SerializerMethodField()
	last_login = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
	first_login = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
	date_joined = serializers.DateTimeField(format="%d-%m-%Y")

	class Meta:
		model = User
		fields = ['id', 'first_name', 'last_name', 'email', 'username', 'phone_number', 'address', 'city', 'state', 'zip', 'country', 'customer_id', 'time_zone', 'language', 'uom', 'subscriptions', 'last_login', 'first_login', 'login_count', 'date_joined']

	def get_subscriptions(self, obj):
		to_send_subscription = []
		subscriptions = Subscription.objects.filter(customer_id=obj.customer_id, device_in_use=True).all()
		serializer_data = SubscriptionSerializer(subscriptions, many=True, read_only=True).data
		for i in serializer_data:
			i['free_trial'] = self.get_free_trial(i.get('imei_no'), i.get('customer_id'))
			# to_send_subscription.append(i)
		return serializer_data

	def get_free_trial(self, imei, customer_id):
		free_trial = FreeTrialModel.objects.filter(imei=imei).last()
		free_ser = FreeTrialSerializer(free_trial, read_only=True).data
		return free_ser

	def get_sim_provider(self, imei):
		sim_mapping = SimMapping.objects.filter(imei=imei).last()
		if sim_mapping:
			return sim_mapping.provider
		return 'Unknown'

class FriMarkersCount(serializers.ModelSerializer):
	class Meta:
		model = FriMarkers
		fields = ['imei']



class GLFriMarkersCount(serializers.ModelSerializer):
	class Meta:
		model = GLFriMarkers
		fields = ['imei']

class DeviceNotReportedSerializers(serializers.ModelSerializer):
	user_credit_card = CreditCardSerializer(many=True)
	last_login = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
	first_login = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
	date_joined = serializers.DateTimeField(format="%d-%m-%Y")
	
	class Meta:
		model = User
		fields = ['id', 'first_name', 'last_name', 'email', 'username', 'phone_number', 'address', 'city', 'state', 'zip', 'country', 'customer_id', 'time_zone', 'language', 'uom', 'user_credit_card', 'last_login', 'first_login', 'login_count', 'date_joined']

	def get_sim_provider(self, imei):
		sim_mapping = SimMapping.objects.filter(imei=imei).last()
		if sim_mapping:
			return sim_mapping.provider
		return 'Unknown'


class EnquiryDetailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = EnquiryDetails
		fields = '__all__'


class FeedbackSupportList(serializers.ModelSerializer):
	free_trial_count = serializers.SerializerMethodField()
	record_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

	class Meta:
		model = FeedBackModel
		fields = ['first_name','last_name','email','feedback','improve_software','missing_features','additional_information','rating','positive','record_date', 'free_trial_count', 'amazon_feedback']

	def get_free_trial_count(self, obj):
		user = User.objects.filter(email=obj.email).last()
		if user:
			free_trial = FreeTrialModel.objects.filter(customer_id=user.customer_id).aggregate(Sum('free_trial_month'))
			return free_trial.get('free_trial_month__sum', 0)
		return '1'