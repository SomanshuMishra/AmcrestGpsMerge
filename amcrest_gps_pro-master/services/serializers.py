from rest_framework import serializers
from django.conf import settings

from services.models import *
from app.models import *




class CountriesSerializer(serializers.ModelSerializer):
	class Meta:
		model = Countries
		fields = '__all__'

class StatesSerializer(serializers.ModelSerializer):
	class Meta:
		model = States
		fields = '__all__'


class TimeZonesSerializer(serializers.ModelSerializer):

	class Meta:
		model = TimeZoneModel
		fields = '__all__'


class LangaugeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Langauges
		fields = '__all__'


class ServicePlanSerializer(serializers.ModelSerializer):
	class Meta:
		model = ServicePlan
		fields = '__all__'


class ServicePlanObdSerializer(serializers.ModelSerializer):
	class Meta:
		model = ServicePlanObd
		fields = '__all__'


class SubscriptionCancelationSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	last_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	email = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	imei = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	cancelation_reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	how_gps_tracker = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	comment = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	start_date = serializers.DateField(required=False, allow_null=True, format="%d-%m-%Y")
	end_date = serializers.DateField(required=False, allow_null=True, format="%d-%m-%Y")
	customer_id = serializers.CharField(required=False, allow_null=True)
	subscription_id = serializers.CharField(required=False, allow_null=True)
	record_date = serializers.DateTimeField(required=False, format="%d-%m-%Y")

	class Meta:
		model = SubscriptionCancelation
		fields = '__all__'

class WebhookSubscriptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = WebhookSubscription
		fields = '__all__'


class DeviceModelSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeviceModel
		fields = '__all__'


class SimMappingSerializer(serializers.ModelSerializer):
	class Meta:
		model = SimMapping
		fields = '__all__'



class PodSimCronSerializer(serializers.ModelSerializer):
	class Meta:
		model = PodSimCron
		fields = '__all__'


class DeviceListingCronSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeviceListingCron
		fields = '__all__'


class ImeiListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subscription
		fields = [
			'imei_no', 'nextBillingDate', 'activated_plan_id', 'activated_plan_description', 'nextBillingDate', 'end_date'
		]


class SimPlanUpdatedRecordSerializer(serializers.ModelSerializer):
	class Meta:
		model = SimPlanUpdatedRecord
		fields = '__all__'


class DeviceFrequencySerializer(serializers.ModelSerializer):
	class Meta:
		model = DeviceFrequency
		fields = '__all__'


class DeviceFrequencyObdSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeviceFrequencyObd
		fields = '__all__'


class AppConfSerializer(serializers.ModelSerializer):
	class Meta:
		model = AppConfiguration
		fields = '__all__'


class DeviceNotReportingAlertSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeviceNotReportingAlert
		fields = '__all__'


class ReviewModelSerializer(serializers.ModelSerializer):
	class Meta:
		model = ReviewModel
		fields = '__all__'


class MobileServiceProviderSerializer(serializers.ModelSerializer):
	class Meta:
		model = MobileServiceProvider
		fields = '__all__'


class AppVersionSerializer(serializers.ModelSerializer):
	class Meta:
		model = AppVersion
		fields = '__all__'
		
class SimMappingSerializer(serializers.ModelSerializer):
	class Meta:
		model = SimMapping
		fields = '__all__'


class DeviceCommandsSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeviceCommands
		fields = '__all__'


class DeviceCommandsListSerializers(serializers.ModelSerializer):
	record_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
	class Meta:
		model = DeviceCommandsList
		fields = '__all__'


class FeedBackPositiveSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(required=True, allow_null=False)
	last_name = serializers.CharField(required=True, allow_null=False)
	email = serializers.CharField(required=True, allow_null=False)
	feedback = serializers.CharField(required=True, allow_null=False)
	rating = serializers.IntegerField(required=True, allow_null=False)

	class Meta:
		model = FeedBackModel
		fields = '__all__'


class FeedBackNegativeSerializers(serializers.ModelSerializer):
	first_name = serializers.CharField(required=True, allow_null=False)
	last_name = serializers.CharField(required=True, allow_null=False)
	email = serializers.CharField(required=True, allow_null=False)
	improve_software = serializers.CharField(required=False, allow_null=True)
	missing_features = serializers.CharField(required=False, allow_null=True)
	additional_information = serializers.CharField(required=False, allow_null=True)
	rating = serializers.CharField(required=True, allow_null=False)

	class Meta:
		model = FeedBackModel
		fields = '__all__'


class FeedBackSkippedSerializer(serializers.ModelSerializer):
	class Meta:
		model = FeedBackSkipped
		fields = '__all__'