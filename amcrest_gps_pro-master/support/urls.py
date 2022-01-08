from django.urls import path, re_path
from django.conf.urls import url
from .views import *
from .user_register import *
from .data_loader_api import *
from .free_trial_apply import *
from .cancel_subscription import *
from .set_limit_pod import *
from .trip_delete import *
import services.webhook_service as ws


urlpatterns = [
		url(r'^customers$', SupportUserView.as_view(), name='user_list'),
		url(r'^customer/update/email$', SupportEmailUpdate.as_view(), name='user_list'),
		url(r'^customer/update/password$', SupportPasswordUpdate.as_view(), name='user_list'),
		url(r'^device/return$', ReturnDeviceView.as_view(), name='device_return'),
		url(r'^resend/activation_mail/(?P<user_id>.+)$', ResendActivationMailView.as_view(), name='resend_activation'),

		url(r'^sim/activate/(?P<imei>.+)$', ActivateSimView.as_view(), name='sim_activation'),
		url(r'^sim/deactivate/(?P<imei>.+)$', DeactivateSimView.as_view(), name='sim_deactivation'),
		url(r'^sim/status/(?P<imei>.+)$', GetSimStatus.as_view(), name='sim_status'),

		url(r'^set/sim/limit$', SetLimitApiView.as_view(), name='set_limit'),

		url(r'^master_password$', MasterPasswordView.as_view(), name='master_password'),
		url(r'^message/send$', MessageSenderView.as_view(), name='message_sender'),

		url(r'^device/registered', ActivatedDeviceCountView.as_view(), name='device_registered'),
		url(r'^device/active$', ActiveDeviceView.as_view(), name='active_device'),
		url(r'^device/subscription/cancelled', SubscriptionCanceledCountView.as_view(), name='subscription_cancelled'),
		url(r'^device/active/total$', TotalActiveDevice.as_view(), name='total_active_device'),
		url(r'^device/rectivated$', ReactivatedDeviceView.as_view(), name='reactivated_device'),
		url(r'^subscription/cancelled', SubscriptionCancelledView.as_view(), name='subscription_cancelled_view'),

		url(r'^user/not_logged_in$', ActivatedNotLoggedView.as_view(), name='user_logged_in'),
		url(r'^user/not/active$', SubscriptionActiveNotLoggedIn.as_view(), name='non_active_user'),
		url(r'^user/device/reporting', ActivatedDeviceNotReportingView.as_view(), name='non_reporting_device'),
		url(r'^replace/imei', ReplaceImeiView.as_view(), name='replace_imei'),

		url(r'^register/user', UserRegisterView.as_view(), name='register_user'),
		url(r'^add/subscription', AddToExistingView.as_view(), name='add_subscription'),

		url(r'^update/username', UpdateUsernameView.as_view(), name='update_username'),

		url(r'^migrate/user', UserLoaderApiView.as_view(), name='load_user'),
		url(r'^migrate/subscription', SubscriptionLoaderApiView.as_view(), name='subscription_loader'),
		url(r'^migrate/zone', ZoneLoaderApiView.as_view(), name='zone_loader'),
		url(r'^migrate/setting', SettingLoaderApiView.as_view(), name='zone_loader'),

		#--------Enquiry
		url(r'^enquiry', UserSupportApiView.as_view(), name='enquiry'),

		#--------Review
		url(r'^manual/review/(?P<customer_id>.+)$', ManualReviewView.as_view(), name='manual_review'),

		#--------Replace Returned IMEI
		url(r'^replace/returned/imei/(?P<customer_id>.+)$', ReplaceReturnedDeviceView.as_view(), name='replace_return_imei'),

		#--------
		url(r'^delete/reports', DeleteReports.as_view(), name='delete_report'),
		url(r'^delete/zone/reports', DeleteZoneReports.as_view(), name='delete_zone_report'),

		#---------------Count Trips
		url(r'^trips/generated', TripsGeneratedCount.as_view(), name='trips_generated'),

		#--------------Update Subscription ID
		url(r'^subscription/update/id$', UpdateSubscriptionIdApiView.as_view(), name='update_subscription_id'),

		#------------Command Operations(CRUD)
		url(r'^imei/commands$', ImeiCommandsSavedApiView.as_view(), name='imei_command_crud'),
		url(r'^device/command_list$', CommandListApiView.as_view(), name='device_command_list'),

		#-----------Device in use deactivate
		url(r'^deactivate/device_in_use/(?P<customer_id>.+)/(?P<imei>.+)', RemoveDeviceInUseView.as_view(), name='device_in_use_deactivate'),

		#---------Email From Support 
		url(r'^send/mail$', SendMailApiView.as_view(), name='email_from_support'),

		#--------Send Batch Message
		url(r'^send/batch/email$', SendBatchMessages.as_view(), name='send_batch_email'),

		#-------Free Trial
		# url(r'update/subscription_id$', UpdateAndCancelSubscription.as_view(), name='update_subscription_id'),
		url(r'apply/free_trial$', ApplyFreeTrialApiView.as_view(), name='apply_free_trial'),

		#-------Feedback List
		url(r'^feedback/list$', FeedbackListApi.as_view(), name='feedback_list'),
		url(r'^feedback/mark/amazon/(?P<email>.+)$', MarkAmzonReviewApi.as_view(), name='amazon_feedback'),

		#-------Cancel Subscription
		url(r'^cancel/subscription$', SubscriptionCancelationView.as_view(), name='cancel_subscription'),

		#--------Delete Trip
		url(r'^trip/delete$', TripDeleteApiView.as_view(), name='trip_delete'),
		
]

