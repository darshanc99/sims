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
    path('returnconfirm/<int:id>',views.returnconfirm,name='returnconfirm'),
    path('viewproduct/',views.viewproduct,name='viewproduct'),
    path('requestproduct/',views.requestproduct,name='requestproduct'),
    path('approveproduct/',views.approveproduct,name='approveproduct'),
    path(r'productconfirm/<int:id>',views.productconfirm,name='productconfirm'),
    path(r'partialconfirm/<int:id>',views.partialconfirm,name='partialconfirm'),
    path(r'canceltransaction/<int:id>',views.canceltransaction,name='canceltransaction'),
    path('pendingprods/',views.pendingprods,name='pendingprods'),
    path('myproduct/',views.myproduct,name='myproduct'),
    path('proddb/',views.proddb,name='proddb'),
    path('add_measure/',views.add_measure,name='add_measure'),
    path('add_category/',views.add_category,name='add_category'),
    path(r'del_unit/<str:name>',views.del_unit,name='del_unit'),
    path(r'del_category/<str:name>',views.del_category,name='del_category'),
    path(r'rejectproduct/<int:id>',views.rejectproduct,name='rejectproduct'),
    path('returnrequest',views.returnrequest,name='returnrequest'),
    path('returnrequestconfirm/<int:id>',views.returnrequestconfirm,name='returnrequestconfirm'),
    path(r'product_accept/<int:id>',views.product_accept,name='product_accept'),
    path('accept_route/',views.accept_route,name='accept_route'),
]
