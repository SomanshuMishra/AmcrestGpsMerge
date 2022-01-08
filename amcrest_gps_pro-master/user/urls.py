from django.urls import path, re_path
from django.conf.urls import url

from .views import *
from .dealer_add_user import DealerUserRegisterView, DealerCustomerList
from .review_system import *
from .invoice import * 
from .subuser import *

urlpatterns = [
		url(r'^register$', UserRegisterView.as_view(), name='register'),
		url(r'^login$', UserLoginView.as_view(), name='login'),
		url(r'^administrator/login$', AdministrationLoginView.as_view(), name='administrator_login'),

		url(r'^change_password/(?P<email>.+)$', ChangePasswordView.as_view(), name='change_password'),
		url(r'^forgot/password/(?P<email>.+)$', ForgotPasswordLinkView.as_view(), name='forgot_password'),
		url(r'^reset/password$', ForgotPasswordChangePasswordView.as_view(), name='reset_password'),
		url(r'^user/profile/(?P<email>.+)$', ProfileView.as_view(), name='user_profile'),
		url(r'^subscribe/devices$', SubscriptionDeviceView.as_view(), name='subscribe_device'),
		url(r'^re-activation/device/reactivate', ReactivateDeviceView.as_view(), name='reactivate_device'),

		url(r'^re-activation/devices/(?P<customer_id>.+)$', ReactivationDeviceView.as_view(), name='reactivation_devices'),
		url(r'^re-activation/obd/devices/(?P<customer_id>.+)$', ReactivationObdDeviceView.as_view(), name='reactivation_devices'),
		url(r'^re-activation/device/info/(?P<customer_id>.+)/(?P<imei>.+)$', ReactivationDeviceInfoView.as_view(), name='reactivation_device_info'),
		
		url(r'^subscription/cancel$', SubscriptionCancelationView.as_view(), name='cancel_subscription'),
		url(r'^credit-card/update$', CreditCardView.as_view(), name='credit_card_update'),

		url(r'^transaction/history/(?P<customer_id>.+)$', TransactionHistoryView.as_view(), name='transaction_history'),
		url(r'^device/update/plan', UpdateDevicePlan.as_view(), name='update_plan'),

		url(r'^username/validation', CheckUsernameExist.as_view(), name='check_username'),

		url(r'^dealer/register', DealerUserRegisterView.as_view(), name='dealer_register'),

		url(r'^review/validation/(?P<customer_id>.+)$', ReviewSystemValidation.as_view(), name='review_validation'),
		url(r'^review/skipped/(?P<customer_id>.+)$', ReviewSkipped.as_view(), name='review_skipped'),
		url(r'^review/rating$', ReviewRating.as_view(), name='review_rating'),
		url(r'^review/final/(?P<customer_id>.+)$', ReviewFinal.as_view(), name='review_final'),

		url(r'^dealer/customers/(?P<customer_id>.+)$', DealerCustomerList.as_view(), name='dealer_customer'),

		url(r'^unsubscribe/mail/(?P<customer_id>.+)$', UnsubscribeMail.as_view(), name='unsubscribe_mail'),

		url(r'^invoice$', InvoiceApiView.as_view(), name='invoice_mailer'),
		url(r'^invoice/download$', InvoiceDownloadApiView.as_view(), name='invoice_download'),

		url(r'^customer/details/(?P<customer_id>.+)$', CustomerDetailsApi.as_view(), name='get_customer_details'),

		url(r'^add/subuser$', SubuserAddApiView.as_view(), name='add_subuser'),

		
]