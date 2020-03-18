from django.db import models

USER_TYPES = (
		("Admin","Admin"),
		("Non-Admin","Non-Admin"),
		("Dealing-Admin","Dealing-Admin"),
	)

# Create your models here.
class useraccounts(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.CharField(max_length=40,primary_key=True)
	phone = models.CharField(max_length=10)
	user_type = models.CharField(max_length=15,choices=USER_TYPES)
	userpassword = models.CharField(max_length=1000)
	userrole = models.CharField(max_length=25,blank=True)
	registered_at = models.DateTimeField(blank=True)
	verified = models.BooleanField(default=False)
	loginstatus = models.BooleanField(default=True)

	def __str__(self):
		return self.email + "-" + self.user_type