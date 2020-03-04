from django.shortcuts import render,redirect
from .models import productlist
from authentication.models import useraccounts
import datetime
# Create your views here.
def addproduct(request):
	logoutStatus= True
	try:
		if request.session['email']:
			print('here')
			if request.method=='POST':
				product_name=request.POST.get('product_name')
				product_category=request.POST.get('product_category')
				product_type=request.POST.get('product_type')
				available_quantity=request.POST.get('avail_quantity')
				arrive=datetime.datetime.now()
				measure_unit=request.POST.get('measure_unit')
				description=request.POST.get('description')
				prod=productlist(product_name,product_category,product_type,available_quantity,arrive,measure_unit,description)
				print(product_category)
				print(prod)
				try:
					if productlist.objects.get(product_name=product_name):
						messages="Product is already present"
						currentEmail = request.session['email']
						currentUser = useraccounts.objects.get(email=currentEmail)
						currentName = currentUser.first_name+" "+currentUser.last_name
						context = {
							'message' : messages,
							'name' : currentName
							}
						return render(request,'products/addproduct.html',context)
				except:
					print('now here')
					prod.save()
					print('also here')
					messages="Product added successfully"
					currentEmail = request.session['email']
					currentUser = useraccounts.objects.get(email=currentEmail)
					currentName = currentUser.first_name+" "+currentUser.last_name
					context = {
						'message' : messages,
						'name' : currentName
						}

					return render(request,'products/addproduct.html',context)		
			else:
				currentEmail = request.session['email']
				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				context = {
					'name' : currentName
					}				
				return render(request,'products/addproduct.html',context)
	except:
		message = "you need to login first"
		context = {
			'message' : message,
			'logoutStatus':logoutStatus
		}
		return render(request,'authentication/login.html',context)					