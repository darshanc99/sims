#Import Dependencies
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	#/
    path('', views.home, name='home'),
    path(r'adduser/',views.newuser,name='newuser'),
    path(r'viewusers/',views.viewusers,name='viewusers'),
    path(r'verify/<str:email>',views.verify,name='verify'),
]