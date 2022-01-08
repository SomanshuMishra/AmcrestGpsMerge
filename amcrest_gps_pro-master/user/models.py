from django.db import models
from django.conf import settings

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model

from user.managers import UserManager

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import ugettext_lazy as _

from django_mysql.models import EnumField
from enumchoicefield import ChoiceEnum, EnumChoiceField
# Create your models here.

import random


class Langauge(ChoiceEnum):
    en = "en"
    de = "de"
    fr = "fr"
    it = "it"
    nl = "nl"
    pt = "pt"
    es = "es"

class UOM(ChoiceEnum):
	one = '1'
	two = '2'


class User(AbstractUser):
	first_name = models.CharField(_('First Name') , max_length = 50, null=True, blank=True)
	last_name = models.CharField(_('Last Name') , max_length=50, null=True, blank=True)
	email = models.EmailField(_('Email Address') , unique=True)
	username = models.CharField(_('Username'), max_length=100, null=True, blank=True)
	phone_number = models.CharField(_('Phone Number'), max_length=13, blank=True, null=True)
	password = models.CharField(_('Password'), max_length=200, null=True, blank=True)
	order_id = models.CharField(_('Order ID'), max_length=20, null=True, blank=True)
	address = models.TextField(_('Address'), null=True, blank=True)
	city = models.CharField(_('City'), max_length=30, null=True, blank=True)
	state = models.CharField(_('State'), max_length=30, null=True, blank=True)
	zip = models.CharField(_('Zip'), max_length=20, blank=True)
	country = models.CharField(_('Country'), max_length=30, null=True, blank=True)
	status = models.IntegerField(_('Status'), null=True)
	company = models.CharField(_('Company'), max_length=30, null=True, blank=True)
	customer_id = models.BigIntegerField(_('Customer ID'), null=True, blank=True)
	subscription_id = models.CharField(_('Subscription ID'), max_length=100, null=True, blank=True)
	transaction_id = models.CharField(_('Transaction ID'), max_length=10, null=True, blank=True)
	assetname = models.CharField(_('Asset Name'), max_length=50,null=True, blank=True)
	subscription_status = models.CharField(_('Subscription Status'), max_length=100, null=True, blank=True)
	topic_id = models.CharField(_('Topic ID'), max_length=30, null=True, blank=True)
	time_zone = models.CharField(_('Time Zone'), max_length=100, null=True, blank=True)
	language = models.CharField(_('Langauges'), max_length=100, null=True, blank=True)
	uom = models.CharField(max_length=10, null=True, default='kms')
	hits = models.FloatField(_('Hits'), null=True, default=1)
	rate = models.FloatField(_('Rate'), null=True, default=9)
	later_time = models.BigIntegerField(_('Later Time'), null=True)
	later_flag = models.BigIntegerField(_('Later Flag'), null=True, default=1)
	last_login = models.DateTimeField(_('Last Login'), null=True)
	first_login = models.DateTimeField(_('First Login'), null=True)
	login_count = models.IntegerField(_('Login Count'), null=True)
	time_zone_description = models.CharField(_('Time Zone Description'), max_length=100, null=True)
	is_dealer = models.BooleanField(default=False)
	is_dealer_user = models.BooleanField(default=False)
	emailing_address = models.EmailField(_('Emailing Address'), null=True)
	mobile_carrier = models.CharField(_('Mobile Carrier'), max_length=50, null=True, blank=True)
	time_format = models.CharField(_('Time Format'), max_length=10, null=False, default='24')
	date_format = models.CharField(_('Date Format'),max_length=30, null=False, blank=False, default='DD/MM/YYYY')
	regenerate_trip = models.BooleanField(default=False)
	subuser = models.BooleanField(default=False)
	primary_user = models.IntegerField(null=True, blank=True)




	objects = UserManager()
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')
		indexes = [
			models.Index(fields=['email', 'username', 'customer_id']),
			models.Index(fields=['email']),
			models.Index(fields=['customer_id']),
		]

	def check_password(self, raw_password):
		return check_password(raw_password, self.password)

	def hash_password(self, raw_password):
		hash_password = make_password(raw_password)
		return hash_password

	def save(self, *args, **kwargs):
		# if not self.username:
		# 	self.username = self.email

		if not self.is_dealer_user:
			self.emailing_address = self.email
		super(User, self).save(*args, **kwargs)

	def __str__(self):
		try:
			return self.first_name+' '+self.last_name
		except(Exception)as e:
			return self.email


@receiver(post_save, sender=User)
def create_hashed_password(sender, instance=None, created=False, **kwargs):
	if created:
		hash_password = make_password(instance.password)
		user = User.objects.filter(id=instance.id).first()
		user.password = hash_password
		# user.customer_id = random.randint(0,1000000)
		user.save()


class CreditCardDetails(models.Model):
	cardholder_name = models.CharField(max_length=100, null=True, blank	=True)
	cvv = models.IntegerField(null=True)
	expiration_date = models.CharField(max_length=10, null=True, blank=True)
	start_number = models.CharField(max_length=7, null=True, blank=True)
	end_number = models.CharField(max_length=5, null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="user_credit_card")

	class Meta:
		managed = True
		app_label = 'user'
		db_table = 'credit_card'
		indexes = [
			models.Index(fields=['user'])
		]



# class PaypalDetails(models.Model):
# 	countryCode = models.CharField(max_length=10, null=True)
# 	email = models.CharField(max_length=200, null=True)
# 	firstName = models.CharField(max_length=200, null=True)
# 	lastName = models.CharField(max_length=200, null=True)
# 	payerId = models.CharField(max_length=200, null=True)
# 	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="user_paypal")

# 	class Meta:
# 		managed = True
# 		app_label = 'user'
# 		db_table = 'paypal_details'
# 		indexes = [
# 			models.Index(fields=['user'])
# 		]


class DealerCustomers(models.Model):
	dealer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dealer')
	customer = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='dealer_customer')

	class Meta:
		managed = True
		app_label = 'user'
		db_table = 'dealer_relation'
		indexes = [
			models.Index(fields=['dealer', 'customer'])
		]
	
	def __str__(self):
		return self.user


class ReviewTable(models.Model):
	customer_id = models.CharField(max_length=50, null=False, blank=False)
	next_review_date = models.DateField(null=True)
	eligible = models.BooleanField(null=True)
	comments = models.TextField(null=True, blank=True)
	rating = models.FloatField(null=True)
	count = models.IntegerField(null=True)
	category = models.CharField(max_length=20)

	class Meta:
		managed = True
		app_label = 'app'
		db_table = 'review_table'
		indexes = [
			models.Index(fields=['customer_id'])
		]

	def __str__(self):
		return self.customer_id


# class 