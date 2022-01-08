from django.db import models

# Create your models here.
class EnquiryDetails(models.Model):
	customer_id = models.CharField(max_length=30, null=False)
	imei = models.CharField(max_length=30, null=True, blank=True)
	message = models.CharField(max_length=500, null=True, blank=True)
	category = models.CharField(max_length=100, null=True, blank=True)
	status = models.BooleanField(default=True)

	def __str__(self):
		return self.customer_id+' : '+self.category


