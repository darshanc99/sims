from django.db import models
from django.utils import timezone
import  datetime


PROD_TYPES=(("consumable","consumable"),
("non-consumable","non-consumable")
	)




# Create your models here.
class master_units(models.Model):
	measure_unit=models.CharField(max_length=20)
	def __str__(self):
		return self.measure_unit


class master_category(models.Model):
	product_category=models.CharField(max_length=50)
	def __str__(self):
		return self.product_category

class productlist(models.Model):
	product_name=models.CharField(max_length=200,primary_key=True)
	product_category=models.CharField(max_length=50)
	product_type=models.CharField(max_length=20,choices=PROD_TYPES)
	available_quantity=models.BigIntegerField()
	arrival_date=models.DateTimeField(blank=True)
	measure_unit=models.CharField(max_length=20)
	description=models.CharField(max_length=300,blank=True)
	def __str__(self):
		return self.product_name + "-" + self.product_category

class productlog(models.Model):
	product_name=models.CharField(max_length=200)
	email=models.CharField(max_length=200)
	quantity=models.BigIntegerField()
	timestamp=models.DateTimeField(blank=True)
	status=models.CharField(max_length=50)
	approved_quantity=models.BigIntegerField(default=None,blank=True)
	def __str__(self):
		return self.product_name + "-" + self.status

class nonconsumable_productlog(models.Model):
	product_name=models.CharField(max_length=200)

	issued_to=models.CharField(max_length=200,blank=True)
	issued_by=models.CharField(max_length=200,blank=True)
	units=models.BigIntegerField(blank=True)
	issue_date=models.DateTimeField(blank=True)
	return_date=models.DateTimeField(blank=True,null=True)
	return_status=models.CharField(max_length=50)
	requested_quantity=models.BigIntegerField(null=True,blank=True)
	def __str__(self):
		return self.product_name+"-"+self.issue_date
