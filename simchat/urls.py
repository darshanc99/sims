from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	#/
	path(r'compose/',views.compose,name='compose'),
	path(r'inbox/',views.inbox,name='inbox'),
	path(r'sent/',views.sent,name='sent'),
	path(r'inbox/<str:id>/',views.inboxview,name='inboxview'),
	path(r'sent/<str:id>/',views.sentview,name='sentview'),
	path(r'deleteinbox/<str:id>/',views.deleteinbox,name='deleteinbox'),
	path(r'deleteoutbox/<str:id>/',views.deleteoutbox,name='deleteoutbox'),
	path(r'in/reply/<str:id>/',views.replyin,name='replyin'),
	path(r'out/reply/<str:id>/',views.replyout,name='replyout'),
]