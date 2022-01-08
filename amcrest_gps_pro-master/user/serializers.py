from rest_framework import serializers
# from django.contrib.auth.models import User
from user.models import *
from django.conf import settings

from app.models import *



class UserWriteSerialzer(serializers.ModelSerializer):
	first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	email = serializers.EmailField(required=True)
	phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	password = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
	order_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	zip = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	status = serializers.IntegerField(required=False, allow_null=True)
	company = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	customer_id = serializers.IntegerField(required=False, allow_null=True)
	subscription_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	transaction_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	assetname = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	subscription_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	topic_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	time_zone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	language = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	uom = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	hits = serializers.FloatField(required=False, allow_null=True)
	rate = serializers.FloatField(required=False, allow_null=True)
	later_time = serializers.IntegerField(required=False, allow_null=True)
	later_flag = serializers.IntegerField(required=False, allow_null=True)
	time_zone_description = serializers.CharField(required=False, allow_null=True)

	class Meta:
		model = User
		fields = '__all__'



class UserSerialzer(serializers.ModelSerializer):
	email = serializers.EmailField(required=False, read_only=True)
	customer_id = serializers.IntegerField(required=False, read_only=True)
	class Meta:
		model = User
		fields = ['id', 'time_zone_description', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'state', 'zip', 'country', 'customer_id', 'company', 'time_zone', 'language', 'uom', 'last_login', 'username', 'emailing_address', 'is_dealer', 'is_dealer_user', 'mobile_carrier', 'time_format', 'regenerate_trip', 'date_format']



class CreditCardSerializer(serializers.ModelSerializer):
	class Meta:
		model = CreditCardDetails
		fields = '__all__'



class SubscriptionInactiveDeviceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subscription
		fields = ['id', 'customer_id', 'imei_no', 'imei_iccid', 'device_listing', 'device_in_use', 'activated_plan_id', 'activated_plan_description']


class UserInfoSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'phone_number', 'order_id', 'address', 'city', 'state', 'zip']


class DealerCustomersSerializer(serializers.ModelSerializer):
	# dealer = serializers.IntegerField(required=True, allow_null=False)
	# customer = serializers.IntegerField(required=True, allow_null=False)

	class Meta:
		model = DealerCustomers
		fields = '__all__'


class DealerUserReadSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'first_name', 'last_name', 'customer_id', 'time_zone', 'last_login', 'username', 'mobile_carrier', 'date_format']

class DealerCustomersReadSerializer(serializers.ModelSerializer):
	# dealer = serializers.IntegerField(required=True, allow_null=False)
	customer = DealerUserReadSerializer()

	class Meta:
		model = DealerCustomers
		fields = '__all__'


class ReviewTableSerializer(serializers.ModelSerializer):
	class Meta:
		model = ReviewTable
		fields = '__all__'


# class PayPalDetailSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = PaypalDetails
# 		fields = '__all__'