from django.shortcuts import render,redirect
from .models import productlist
from authentication.models import useraccounts
import datetime
import hashlib
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
					
					prod.save()
					all_products=productlist.objects.all().order_by("product_name")
					messages="Product added successfully"
					currentEmail = request.session['email']
					currentUser = useraccounts.objects.get(email=currentEmail)
					currentName = currentUser.first_name+" "+currentUser.last_name
					context = {
						'all_products':all_products,
						'message' : messages,
						'name' : currentName
						}

					return render(request,'products/addproduct.html',context)		
			else:
				all_products=productlist.objects.all().order_by("product_name")
				currentEmail = request.session['email']
				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				context = {
					'all_products':all_products,
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

def addquantity(request):
	logoutStatus=True
	try:
		print(request.session['email'])
		if request.session['email']:

			print("alssoooo")
			if request.method=='POST':
				print("here")
				names=request.POST.get('product_category')
				quantity=request.POST.get('quantity')
				details=productlist.objects.get(product_name=names)
				
				ans=int(details.available_quantity)+int(quantity)
				print(ans)  
				all_products=productlist.objects.all().order_by("product_name")
				print(all_products)
				currentEmail = request.session['email']
				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				productlist.objects.filter(product_name=names).update(available_quantity=ans)
				context = {
					'messages':'the product quantity is updated',
					'name' : currentName,
					'all_products':all_products
					}				
				return render(request,'products/addquantity.html',context)
			else:
				all_products=productlist.objects.all().order_by("product_name")
				
				currentEmail = request.session['email']
				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				context = {
					'name' : currentName,
					'all_products':all_products
					}				
				return render(request,'products/addquantity.html',context)
	except:
		
		message = "you need to login first"
		context = {
			'message' : message,
			'logoutStatus':logoutStatus
		}
		return render(request,'authentication/login.html',context)

def removeproduct(request):

	logoutStatus=True
	try:

		if request.session['email']:
			email=request.session['email']
			if request.method=='POST':
				print("herewego")
				names=request.POST.get('product_list')
				print(names)
				password=request.POST.get('pass')
				password = hashlib.sha256(password.encode()).hexdigest()
				print("norttrfddf")
				if useraccounts.objects.get(email=email):
						user = useraccounts.objects.get(email=email)
						
						if user.userpassword == password:
							print('heereeeswres')
							productlist.objects.filter(product_name=names).delete()
							
							messages = "Product removed !"
							all_products=productlist.objects.all().order_by("product_name")
							context={
							'all_products': all_products,
							'messages': messages
							}

							return render(request,'products/removeproduct.html',context)

						else:
							messages='password does not match'
							all_products=productlist.objects.all().order_by("product_name")
							context={
							'all_products':all_products,
							'messages':messages
							}
							return render(request,'products/removeproduct.html',context)
				else:
					messages='email does not match'
					all_products=productlist.objects.all().order_by("product_name")
					context={
					'all_products':all_products,
					'messages':messages
					}
					return render(request,'products/removeproduct.html',context)

					
			else:
				all_products=productlist.objects.all().order_by("product_name")
				context={
				'all_products':all_products
				}
				return render(request,'products/removeproduct.html',context)
	except:
		message='you need to login first'
			
		context={
				
		'message':message,
		'logoutStatus':logoutStatus
			}
		return render(request,'authentication/login.html',context)


def viewproduct(request):
	logoutStatus=True
	if request.session['email']:
		all_products=productlist.objects.all().order_by("product_name")
		currentEmail = request.session['email']
		currentUser = useraccounts.objects.get(email=currentEmail)
		currentName = currentUser.first_name+" "+currentUser.last_name
		context={
			'name':currentName,
			'all_products':all_products
			}
		return render(request,'products/products.html',context)
	else:
		message='you need to login first'
			
		context={
				
		'message':message,
		'logoutStatus':logoutStatus
			}
		return render(request,'authentication/login.html',context)


				

