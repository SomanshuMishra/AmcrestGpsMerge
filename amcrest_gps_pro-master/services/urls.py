from django.urls import path, re_path
from django.conf.urls import url
from .views import *
from .update_record import *
from .feedback import *
import services.webhook_service as ws
import services.data_loader as loader
from services.mongo_dump import *


urlpatterns = [
		url(r'^countries$', CountriesView.as_view(), name='countries'),
		url(r'^country/(?P<country_id>.+)/states$', StatesView.as_view(), name='states'),
		url(r'^timezones$', TimeZoneView.as_view(), name='time_zone'),
		url(r'^langauges$', LangaugesView.as_view(), name='langauges'),
		url(r'^imei_validation/(?P<imei>.+)', ImeiValidationView.as_view(), name='imei_validation'),
		url(r'^service_plan$', ServicePlanView.as_view(), name='service_plan'),
		url(r'^service_plan/obd$', ServicePlanObdView.as_view(), name='service_plan_obd'),
		url(r'^cancel/validate/(?P<imei>.+)', CancelSubscriptionValidation.as_view(), name='cancel_imei_validation'),
		url(r'^card/validate/(?P<customer_id>.+)/(?P<card_number>.+)', CardValidateView.as_view(), name='validate_card_number'),
		url(r'^webhook$', ws.WebHookView.as_view(), name='webhook'),
		url(r'^device_model$', DeviceModelView.as_view(), name='device_models'),
		url(r'^imei/list/(?P<customer_id>.+)$', UserImeiList.as_view(), name='imei_list'),
		url(r'^device_frequency/list$', DeviceFrequencyView.as_view(), name='device_frequency_list'),
		url(r'^device_frequency/list/obd$', DeviceFrequencyObdView.as_view(), name='device_frequency_obd_list'),

		url(r'^mobile/service_provider$', MobileServiceProviderView.as_view(), name='mobile_service_provider'),

		url(r'^combine/plan/list$', CombinePlanList.as_view(), name='combine_plan_list'),

		url(r'^convert/gpx$', GpxToJsonView.as_view(), name='convert_gpx'),

		url(r'^check/email/(?P<email>.+)', CheckEmailExist.as_view(), name='check_email'),

		#-----------Data Loader

		url(r'^load/user', loader.UserLoader.as_view(), name='user_loader'),
		url(r'^load/subscription', loader.SubscriptionLoader.as_view(), name='subscription_loader'),
		url(r'^load/settings', loader.SettingLoader.as_view(), name='settings_loader'),
		url(r'^load/report', loader.ReportLoader.as_view(), name='report_loader'),
		url(r'^load/zone', loader.ZoneLoader.as_view(), name='zone_loader'),

		url(r'^notice', NoticeView.as_view(), name='notice_view'),
		url(r'^important/notice$', ImportantNoticeApiView.as_view(), name='important_notice'),


		#--------Mongo Dump
		url(r'^dump/user_trip/(?P<imei>.+)', DumpUserTrip.as_view(), name='dump_user_trip'),

		#--------Update Record
		url(r'^update/record', UpdateRecord.as_view(), name='update_record'),

		#-----Dealer Info
		url(r'^dealer/info/(?P<customer_id>.+)$', DealerInfo.as_view(), name='dealer_info'),

		#------location Constant
		url(r'^location/constant$', LocationConstant.as_view(), name='location_constant'),

		#--------Application Vesion
		url(r'^app/version$', AppVersionView.as_view(), name='app_version'),

		#---------Frequency
		url(r'^frequency/list/(?P<imei>.+)$', FrequencyListForImei.as_view(), name='frequency_list'),

		#-------------Get command
		url(r'^command/(?P<imei>.+)$', GetCommandApiView.as_view(), name='get_command'),

		#-----------Service Plan ALL
		url(r'^all/service/plans', AllServicePlan.as_view(), name='all_service_plan'),

		#---------Feedback
		url(r'^feedback/validate/user', ValidateEmailApiView.as_view(), name='validate_user'),
		url(r'^feedback/validate/registration', CheckRegisteredDate.as_view(), name='registration_validate'),
		url(r'^feedback/positive', PositiveFeedbackApiView.as_view(), name='positive_feedback'),
		url(r'^feedback/negative', NegativeFeedbackApiView.as_view(), name='positive_feedback'),
		url(r'^feedback/skip$', FeedBackSkippedApiView.as_view(), name='feedback_skip'),


		#-------Server Status
		url(r'^server/status$', ServerStatusApiView.as_view(), name='server_status'),

		#-------Sim mapping
		url(r'^sim/mapping$', SimMappingApiView.as_view(), name='sim_mapping'),

		
		
]