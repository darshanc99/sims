from django.db import models

# Create your models here.
class useraccounts(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.CharField(max_length=40,primary_key=True)
	phone = models.CharField(max_length=10)
	user_type = models.CharField(max_length=25)
	userpassword = models.CharField(max_length=1000)
	userrole = models.CharField(max_length=25,blank=True)
	registered_at = models.DateTimeField(blank=True)
	verified = models.BooleanField(default=False)
	loginstatus = models.BooleanField(default=True)
	accountstatus = models.BooleanField(default=True)

	def __str__(self):
		return self.email + "-" + self.user_type

class master_user_types(models.Model):
	user_type = models.CharField(max_length=25)
	deletestatus = models.BooleanField(default=True)
	def __str__(self):
		return self.user_type
