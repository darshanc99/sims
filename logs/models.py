from django.db import models
from django.utils import timezone
import  datetime
from authentication.models import useraccounts
from products.models import productlist 

# Create your models here.
class sessionlogs(models.Model):
	email = models.CharField(max_length=40)
	timestamp = models.DateTimeField(blank=True,default=None)
	message = models.CharField(max_length = 50,blank=True)

	def __str__(self):
		return self.email 