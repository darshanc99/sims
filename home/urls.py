#Import Dependencie
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	#/
    path('', views.home, name='home'),
    path(r'adduser/',views.newuser,name='newuser'),
    path(r'userbase/',views.userbase,name='userbase'),
    path(r'newusertype/',views.newusertype,name='newusertype'),
    path(r'deleteusertype/<str:usertype>',views.deleteusertype,name='deleteusertype'),
    path(r'verify/<str:email>',views.verify,name='verify'),
    path(r'delete/<str:email>',views.deleteuser,name='deleteuser'),
    path(r'freeze/<str:email>',views.freezeuser,name='freezeuser'),
    path(r'unfreeze/<str:email>',views.unfreezeuser,name='unfreezeuser'),
    path(r'edit/<str:email>',views.edituser,name='edituser'),
    path(r'edituserpassword/<str:email>',views.edituserpassword,name='edituserpassword'),
    path(r'error/',views.error,name='error'),
    path(r'filter/',views.filter,name='filter'),
    path(r'report/',views.report,name='report'),
    path(r'report/export/',views.export,name='export'),
    path(r'report/export/<str:start>/<str:end>/',views.exportcsv,name='exportcsv'),
    path(r'offline/<str:email>/',views.offline,name='offline'),
]
