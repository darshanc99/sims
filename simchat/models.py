from django.db import models

# Create your models here.
class simmessage(models.Model):
	sender = models.CharField(max_length=40)
	receiver = models.CharField(max_length=40)
	subject = models.TextField(max_length=100)
	body = models.TextField(max_length=1000)
	read = models.BooleanField(default=False)
	intrashed = models.BooleanField(default=False)
	outtrashed = models.BooleanField(default=False)
	timestamp = models.DateTimeField(blank=True,default=None)
	
	def __str__(self):
		return self.uid + ' - ' + self.subject	