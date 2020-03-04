from django.db import models
from django.utils import timezone
import  datetime
CATEGORIES=(
	("stationery","stationery"),
	("electronics","electronics"),
	("others","others")
	)

PROD_TYPES=(("consumable","consumable"),
("non-consumable","non-consumable")
	)

MEASUREMENT=(("kilogaram","kilogram"),
("metres","metres"),("inches","inches"),
("units","units")
	)
	

# Create your models here.
class productlist(models.Model):
	product_name=models.CharField(max_length=200,primary_key=True)
	product_category=models.CharField(max_length=50,choices=CATEGORIES,default='others')
	product_type=models.CharField(max_length=20,choices=PROD_TYPES)
	available_quantity=models.BigIntegerField()
	arrival_date=models.DateTimeField(default=datetime.datetime.now(),blank=True) 
	measure_unit=models.CharField(max_length=20,choices=MEASUREMENT) 
	description=models.CharField(max_length=300,blank=True)		
	def __str__(self):
		return self.product_name + "-" + self.product_category  