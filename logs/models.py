from django.db import models
from django.utils import timezone
import  datetime
from authentication.models import useraccounts

# Create your models here.
class sessionlogs(models.Model):
	email = models.CharField(max_length=40)
	timestamp = models.DateTimeField(blank=True,default=None)
	message = models.CharField(max_length = 50,blank=True)
#	login_on = models.DateTimeField(blank=True,default=None)
#	logout_on = models.DateTimeField(blank=True,default=None,null=True)

	def __str__(self):
		return self.email 