from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	#/
    path('addproduct/', views.addproduct, name='addproduct'),
    path('addquantity/', views.addquantity, name='addquantity'),
    path('removeproduct/',views.removeproduct,name='removeproduct')
   
]