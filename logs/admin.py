from django.contrib import admin
from .models import sessionlogs

# Register your models here.
model = [sessionlogs]
admin.site.register(model)