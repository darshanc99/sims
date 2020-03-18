#Import Dependencies
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	#/
    path('', views.home, name='home'),
    path(r'adduser/',views.newuser,name='newuser')
]