from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	#/
    path('addproduct/', views.addproduct, name='addproduct'),
    path('addquantity/', views.addquantity, name='addquantity'),
    path('removeproduct/',views.removeproduct,name='removeproduct'),
    path('routeproduct/',views.routeproduct,name='routeproduct'),
    path('edprod/<str:name>',views.edprod,name='edprod'),
    path('returnproduct',views.returnproduct,name='returnproduct'),
    path('returnconfirm/<str:name>,<int:id>',views.returnconfirm,name='returnconfirm'),
    path('viewproduct/',views.viewproduct,name='viewproduct'),
    path('requestproduct/',views.requestproduct,name='requestproduct'),
    path('approveproduct/',views.approveproduct,name='approveproduct'),
    path(r'productconfirm/<int:id>,<str:quantity>',views.productconfirm,name='productconfirm'),
    path(r'partialconfirm/<int:id>',views.partialconfirm,name='partialconfirm'),
    path(r'canceltransaction/<int:id>',views.canceltransaction,name='canceltransaction'),
    path('pendingprods/',views.pendingprods,name='pendingprods'),
    path('myproduct/',views.myproduct,name='myproduct')

]