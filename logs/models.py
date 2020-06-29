from django.db import models
from django.utils import timezone
import  datetime
from authentication.models import useraccounts
from products.models import productlist

# Create your models here.
class sessionlogs(models.Model):
	email = models.CharField(max_length=40)
	timestamp = models.DateTimeField(blank=True,default=None)
	message = models.CharField(max_length = 100,blank=True)

	def __str__(self):
		return self.email

class product_transaction_logs(models.Model):
	email = models.CharField(max_length=40)
	timestamp = models.DateTimeField(blank=True,default=None)
	message = models.CharField(max_length = 500,blank=True)

	def __str__(self):
		return self.email

class product_operationlogs(models.Model):
	product_name=models.CharField(max_length=100)
	timestamp = models.DateTimeField(blank=True,default=None)
	operation = models.CharField(max_length=100,default=None)
	quantity = models.BigIntegerField()
	initial_quantity = models.BigIntegerField()
	final_quantity = models.BigIntegerField()
	issued_by = models.CharField(max_length=100)

	def __str__(self):
		return self.product_name