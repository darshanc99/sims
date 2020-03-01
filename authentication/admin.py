from django.contrib import admin
from .models import useraccounts

# Register your models here.
model = [useraccounts]
admin.site.register(model)