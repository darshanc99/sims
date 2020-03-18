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
    path(r'delete/<str:email>',views.deleteuser,name='deleteuser'),
    path(r'freeze/<str:email>',views.freezeuser,name='freezeuser'),
    path(r'unfreeze/<str:email>',views.unfreezeuser,name='unfreezeuser'),
    path(r'edit/<str:email>',views.edituser,name='edituser'),
]