from django.shortcuts import render,redirect
from .models import productlist,productlog,nonconsumable_productlog,master_units,master_category
from authentication.models import useraccounts
from logs.models import sessionlogs,product_transaction_logs,product_operationlogs
from simchat.models import simmessage
from django.utils import timezone
import datetime
import random
import string
import hashlib

# Create your views here.
#Add product
def addproduct(request):
	logoutStatus= True
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			all_units=master_units.objects.all()
			all_category=master_category.objects.all()
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context = {
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'dealing_admin' : dealing_admin,
					'verified':user.verified,

					'name' : currentName
						}
				return render(request,'home/base.html',context)

			if request.method=='POST':
				product_name=request.POST.get('product_name')
				product_category=request.POST.get('product_category')
				product_type=request.POST.get('product_type')
				available_quantity=request.POST.get('avail_quantity')
				arrive=datetime.datetime.now()
				measure_unit=request.POST.get('measure_unit')
				description=request.POST.get('description')
				prod=productlist(product_name,product_category,product_type,available_quantity,arrive,measure_unit,description)

				try:
				#product rejected if same name
					if productlist.objects.get(product_name=product_name):
						messages="Product is already present"
						currentEmail = request.session['email']
						currentUser = useraccounts.objects.get(email=currentEmail)
						currentName = currentUser.first_name+" "+currentUser.last_name
						context = {
							'admin':admin,
							'dealing_admin':dealing_admin,
							'non_admin':non_admin,
							'message' : messages,
							'all_category':all_category,
							'all_products':all_products,
							'all_units':all_units,
							'verified':user.verified,
							'name' : currentName
							}
						return render(request,'products/addproduct.html',context)
				except:
					# product accepted
					prod.save()
					all_products=productlist.objects.all().order_by("product_name")
					messages="Product added successfully"
					currentEmail = request.session['email']
					currentUser = useraccounts.objects.get(email=currentEmail)
					currentName = currentUser.first_name+" "+currentUser.last_name
					context = {
						'admin':admin,
						'dealing_admin':dealing_admin,
						'non_admin':non_admin,
						'all_products':all_products,
						'verified':user.verified,
						'all_category':all_category,
						'all_products':all_products,
						'all_units':all_units,
						'message' : messages,
						'name' : currentName
						}
					now = datetime.datetime.now(tz=timezone.utc)
					email=request.session['email']

					accounts = product_transaction_logs(email =email,timestamp = now,message="New Product added "+" ("+ product_name+ ")")
					accounts.save()
					content= product_operationlogs(product_name=product_name,timestamp=now,operation="addition",quantity=int(available_quantity),initial_quantity=0,final_quantity=int(available_quantity),issued_by=email)
					content.save()
					return render(request,'products/addproduct.html',context)
			else:
				#displaying the page
				all_products=productlist.objects.all().order_by("product_name")
				currentEmail = request.session['email']
				all_units=master_units.objects.all()

				all_category=master_category.objects.all()

				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				context = {
					'admin':admin,
					'dealing_admin':dealing_admin,
					'verified':user.verified,
					'non_admin':non_admin,
					'all_units':all_units,
					'all_category':all_category,
					'all_products':all_products,
					'name' : currentName
					}
				return render(request,'products/addproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			#if user not logged in
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')

#Increase Quantity of the product in the inventory
def addquantity(request):
	logoutStatus=True
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context = {
					'logoutStatus' : False,
					'admin' : admin,
					'verified':user.verified,
					'non_admin' : True,
					'dealing_admin' : dealing_admin,

					'name' : currentName
						}
				return render(request,'home/base.html',context)

			if request.method=='POST':
				names=request.POST.get('product_category')
				quantity=request.POST.get('quantity')
				details=productlist.objects.get(product_name=names)
				ans=int(details.available_quantity)+int(quantity)
				all_products=productlist.objects.all().order_by("product_name")
				productlist.objects.filter(product_name=names).update(available_quantity=ans)
				context = {
					'admin':admin,
					'dealing_admin':dealing_admin,
					'non_admin':non_admin,
					'verified':user.verified,
					'messages':'the product quantity is updated',
					'name' : currentName,
					'all_products':all_products
					}
				now = datetime.datetime.now(tz=timezone.utc)
				email=request.session['email']
				accounts = product_transaction_logs(email =email,timestamp = now,message="product ("+names +")" + " quantity increased (+"+quantity+")")
				accounts.save()
				data=product_operationlogs.objects.filter(product_name=names).order_by('timestamp').last()
				value=int(quantity)+data.final_quantity
				content= product_operationlogs(product_name=names,timestamp=now,operation="addition",quantity=int(quantity),initial_quantity=int(data.final_quantity),final_quantity=value,issued_by=email)
				content.save()
				return render(request,'products/addquantity.html',context)
			else:
				all_products=productlist.objects.all().order_by("product_name")
				context = {
					'admin':admin,
					'dealing_admin':dealing_admin,
					'non_admin':non_admin,
					'name' : currentName,
					'verified':user.verified,
					'all_products':all_products
					}
				return render(request,'products/addquantity.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')
		return render(request,'authentication/login.html',context)

#Remove Product from the inventory
def removeproduct(request):
	logoutStatus=True
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			#storing all the product not used 
			del_list=[]
			for data in all_products:
				content=productlog.objects.filter(product_name=data.product_name)
				if content:
					continue
				else:
					del_list.append(data.product_name)
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context = {
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'dealing_admin' : dealing_admin,
					'verified':user.verified,

					'name' : currentName
						}
				return render(request,'home/base.html',context)
			if request.method=='POST':
				# checking if  password matches
				names=request.POST.get('product_list')
				password=request.POST.get('pass')
				password = hashlib.sha256(password.encode()).hexdigest()
				if useraccounts.objects.get(email=request.session['email']):
						if user.userpassword == password:
							productlist.objects.filter(product_name=names).delete()
							messages = "Product removed !"
							all_products=productlist.objects.all().order_by("product_name")
							context={
							'admin':admin,
							'dealing_admin':dealing_admin,
							'non_admin':non_admin,
							'messages':messages,
							'name':currentName,
							'all_products':all_products,
							'del_list':del_list,
							'verified':user.verified
							}
							now = datetime.datetime.now(tz=timezone.utc)
							email=request.session['email']
							accounts = product_transaction_logs(email =email,timestamp = now,message="Product Removed ("+names+")")
							accounts.save()
							product_operationlogs.objects.filter(product_name=names).delete()
							return render(request,'products/removeproduct.html',context)
						else:
							#password did not match
							messages = "Password do not match !"
							all_products=productlist.objects.all().order_by("product_name")
							context={
							'admin':admin,
							'dealing_admin':dealing_admin,
							'non_admin':non_admin,
							'messages':messages,
							'name':currentName,
							'verified':user.verified,
							'all_products':all_products,
							'del_list':del_list
							}
							return render(request,'products/removeproduct.html',context)
				else:
					messages='email does not match'
					context={
						'admin':admin,
						'dealing_admin':dealing_admin,
						'non_admin':non_admin,
						'verified':user.verified,
						'name':currentName,
						'all_products':all_products,
						'del_list':del_list
						}
					return render(request,'products/removeproduct.html',context)
			else:
				context={
						'admin':admin,
						'dealing_admin':dealing_admin,
						'non_admin':non_admin,
						'name':currentName,
						'verified':user.verified,
						'all_products':all_products,
						'del_list':del_list
						}
				return render(request,'products/removeproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')

#View Product
def viewproduct(request):
	logoutStatus=True
	admin=False
	dealing_admin=False
	non_admin=False
	try:
		if request.session['email']:
			user=useraccounts.objects.get(email=request.session['email'])
			if user.user_type=='Admin':
				admin=True
			elif user.user_type=='Dealing-Admin':
				dealing_admin=True
			all_products=productlist.objects.filter(product_type="consumable").order_by("product_name")
			noncon_product=productlist.objects.filter(product_type="non-consumable").order_by("product_name")
			currentEmail = request.session['email']
			currentUser = useraccounts.objects.get(email=currentEmail)
			currentName = currentUser.first_name+" "+currentUser.last_name
			context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':False,
				'verified':user.verified,
				'name':currentName,
				'all_products':all_products,
				'noncon_product':noncon_product
					}
			return render(request,'products/products.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')

#Updating the product details(editing product)
def routeproduct(request):
	logoutStatus=True
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.filter(product_type="consumable").order_by("product_name")
			noncon_product=productlist.objects.filter(product_type="non-consumable").order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context = {
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'dealing_admin' : dealing_admin,
					'verified':user.verified,

					'name' : currentName
						}
				return render(request,'home/base.html',context)
			if request.method=='POST':
				old_name=request.POST.get('product_list')
				product_category=request.POST.get('product_category')
				product_type=request.POST.get('product_type')
				available_quantity=request.POST.get('avail_quantity')
				measure_unit=request.POST.get('measure_unit')
				feed=productlist.objects.filter(product_name=old_name).first()
				#checking if entered quantity is same or different from given
				if int(feed.available_quantity) > int(available_quantity):
					new_data=int(feed.available_quantity) - int(available_quantity)
					content= product_operationlogs(product_name=old_name,timestamp=datetime.datetime.now(tz=timezone.utc),operation="subtraction",quantity=new_data,initial_quantity=int(feed.available_quantity),final_quantity=available_quantity,issued_by=request.session['email'])
					content.save()
				elif int(feed.available_quantity) < int(available_quantity):
					new_data= int(available_quantity)-int(feed.available_quantity)
					content= product_operationlogs(product_name=old_name,timestamp=datetime.datetime.now(tz=timezone.utc),operation="addition",quantity=new_data,initial_quantity=int(feed.available_quantity),final_quantity=available_quantity,issued_by=request.session['email'])
					content.save()
				productlist.objects.filter(product_name=old_name).update(product_category=product_category,available_quantity=available_quantity,measure_unit=measure_unit,product_type=product_type)
				message='Product details updated '
				all_products=productlist.objects.filter(product_type="consumable").order_by("product_name")
				noncon_product=productlist.objects.filter(product_type="non-consumable").order_by("product_name")
				context={
							'admin':admin,
							'dealing_admin':dealing_admin,
							'non_admin':non_admin,
							'message':message,
							'verified':user.verified,
							'name':currentName,
							'all_products':all_products,
							'noncon_product':noncon_product
							}
				now = datetime.datetime.now(tz=timezone.utc)
				email=request.session['email']
				accounts = product_transaction_logs(email =email,timestamp = now,message="Product details Updated For"+old_name)
				accounts.save()
				return render(request,'products/products.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')

#edit page for the selected product
def edprod(request,name):
	logoutStatus=True
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context = {
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'dealing_admin' : dealing_admin,
					'verified':user.verified,

					'name' : currentName
						}
				return render(request,'home/base.html',context)
			all_products=productlist.objects.filter(product_name=name)
			all_units=master_units.objects.all()
			all_category=master_category.objects.all()
			context={
					'admin':admin,
					'dealing_admin':dealing_admin,
					'non_admin':non_admin,
					'all_units':all_units,
					'all_category':all_category,
					'verified':user.verified,
					'name':currentName,
					'all_products':all_products
				}
			return render(request,'products/editproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')

# rendering the request product page
def requestproduct(request):
	admin=False
	non_admin=False
	dealing_admin=False
	logoutStatus=True
	try:
		if request.session['email']:
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Non-Admin':
				non_admin = True
				
			else:
				dealing_admin = True
			if request.method=='POST':
				product_name=request.POST.get('product_category')
				quantity=request.POST.get('quantity')
				proddetails=productlist.objects.get(product_name=product_name)
				if((int(quantity)>int(proddetails.available_quantity) or int(quantity)<=0) and user.verified):
					context={
					'admin':admin,
					'non_admin':non_admin,
					'dealing_admin':dealing_admin,
					'all_products':all_products,
					'verified':user.verified,
					'messages':'Please request for proper quantity',
					'name':currentName,
					'logoutStatus':False
							}
					return render(request,'products/requestproduct.html',context)
				else:
					times=datetime.datetime.now(tz=timezone.utc)
					datas=productlog(product_name=product_name,email=request.session['email'],quantity=quantity,timestamp=times,status='pending',approved_quantity=-1)
					datas.save()
					accounts = product_transaction_logs(email =request.session['email'],timestamp = times,message="Product requested " +product_name+" Amount :"+quantity)
					accounts.save()
					context={
					'admin':admin,
					'non_admin':non_admin,
					'dealing_admin':dealing_admin,
					'all_products':all_products,
					'verified':user.verified,
					'messages':'The request is sent you wll be notified once product is approved',
					'name':currentName,
					'logoutStatus':False
							}
					return render(request,'products/requestproduct.html',context)
			else:
				logoutStatus=False
				context={
				'admin':admin,
				'non_admin':non_admin,
				'dealing_admin':dealing_admin,
				'all_products':all_products,
				'verified':user.verified,

				'name':currentName,
				'logoutStatus':False
					}
				return render(request,'products/requestproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')


# rendering approve product page
def approveproduct(request):
	admin=False
	non_admin=False
	dealing_admin=False
	logoutStatus=True
	try:
		if request.session['email']:
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
				
			else:
				context = {
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,
					'name' : currentName
						}
				return render(request,'home/base.html',context)
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			all_products=productlog.objects.filter(status='pending')
			prodnew=productlist.objects.all().order_by("product_name")
			rejprod=productlog.objects.filter(status='denied')
			#calculating total requested quantity for all products
			item_quant={}
			for data in prodnew:
				sum=0
				content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
				for con in content:
					sum=sum+con.quantity
				if sum==0:
					continue
				else:
					item_quant[data.product_name]=int(sum)	
			data2=productlog.objects.filter(status='approved').union(productlog.objects.filter(status='partially approved'))
			data3=nonconsumable_productlog.objects.filter(return_status='true')
			non_conprod=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='true')
			non_accept=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='false')
			context={
			'dealing_admin':dealing_admin,
			'admin':admin,
			'rejprod':rejprod,
			'non_admin':non_admin,
			'non_accept':non_accept,
			'name':currentName,
			'verified':user.verified,
			'item_quant':item_quant,
			'all_products':all_products,
			'non_conprod':non_conprod,
			'data2':data2,
			'data3':data3,
			'prodnew':prodnew,
			'logoutStatus':False
			}
			return render(request,'products/approveproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')
# completely confirming the product
def productconfirm(request,id):
	admin=False
	non_admin=False
	dealing_admin=False
	logoutStatus=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,
					'name' : currentName}
				return render(request,'home/base.html',context)
			dummy=productlog.objects.get(id=id)
			product_name=dummy.product_name
			proddata=productlist.objects.get(product_name=dummy.product_name)
			quantity=int(dummy.quantity)

			if(quantity>proddata.available_quantity):
				all_products=productlog.objects.filter(status='pending')
				data2=productlog.objects.filter(status='approved').union(productlog.objects.filter(status='partially approved'))
				rejprod=productlog.objects.filter(status='denied')
				data3=nonconsumable_productlog.objects.filter(return_status='true')
				non_conprod=nonconsumable_productlog.objects.filter(return_status='false')
				prod=productlist.objects.get(product_name=product_name)
				sizes=prod.available_quantity
				prodnew=productlist.objects.all().order_by("product_name")
				item_quant={}
				for data in prodnew:
					sum=0
					content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
					for con in content:
						sum=sum+con.quantity
					if sum==0:
						continue
					else:
						item_quant[data.product_name]=int(sum)
				context={
				'dealing_admin':dealing_admin,
				'admin':admin,
				'non_admin':non_admin,
				'name':currentName,
				'verified':user.verified,
				'non_conprod':non_conprod,
				'item_quant':item_quant,
				'messages':'The product cannot be approved less quantity available',
				'all_products':all_products,
				'data2':data2,
				'rejprod':rejprod,
				'data3':data3,
				'prodnew':prodnew

				}
				return render(request,'products/approveproduct.html',context)
			
			email=dummy.email
			if(proddata.product_type=='non-consumable'):
				#generating the serial key for non-consumable product
				ser_list=[]
				comp_data=nonconsumable_productlog.objects.all()
				for item in comp_data:
					ser_list.append(item.product_serial_no)
				for i in range(quantity):
					key=''
					for k in range(2):
						key+=random.choice(string.ascii_uppercase)
					for j in range(2):
						key+=random.choice(string.digits)
					for l in range(2):
						key+=random.choice(string.ascii_uppercase)
					while(True):
						if key in ser_list:
							key=''
							for k in range(0,2):
								key+=random.choice(string.ascii_uppercase)
							for j in range(0,2):
								key+=random.choice(string.digits)
							for l in range(0,2):
								key+=random.choice(string.ascii_uppercase)
						else:
							adding=nonconsumable_productlog(product_name=dummy.product_name,issued_to=email,issued_by=request.session['email'],units=1,issue_date=datetime.datetime.now(tz=timezone.utc),return_status='false',requested_quantity=1,return_request='false',product_serial_no=key,product_accepted='false')
							adding.save()
							ser_list.append(key)
							break
			message="Product "+product_name+" "+ "with quantity" +"("+str(quantity)+")"+ " Completely approved to  "+email
			productlog.objects.filter(id=id).update(status='approved',timestamp=datetime.datetime.now(tz=timezone.utc),approved_quantity=quantity,issued_by=request.session['email'])
			all_products=productlog.objects.filter(status='pending')
			data2=productlog.objects.filter(status='approved').union(productlog.objects.filter(status='partially approved'))
			rejprod=productlog.objects.filter(status='denied')
			data3=nonconsumable_productlog.objects.filter(return_status='true')
			non_conprod=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='true')
			non_accept=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='false')
			prod=productlist.objects.get(product_name=product_name)
			sizes=prod.available_quantity
			prodnew=productlist.objects.all().order_by("product_name")
			productlist.objects.filter(product_name=product_name).update(available_quantity=sizes-int(quantity))
			element=product_operationlogs.objects.filter(product_name=product_name).order_by('timestamp').last()
			value=element.final_quantity - int(quantity)
			content= product_operationlogs(product_name=product_name,timestamp=datetime.datetime.now(tz=timezone.utc),operation="subtraction",quantity=int(quantity),initial_quantity=int(element.final_quantity),final_quantity=value,issued_by=email)
			content.save()
			item_quant={}
			for data in prodnew:
				
				sum=0
				content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
				for con in content:
					sum=sum+con.quantity
				if sum==0:
					continue
				else:
					item_quant[data.product_name]=int(sum)
			context={
			'dealing_admin':dealing_admin,
			'admin':admin,
			'non_admin':non_admin,
			'name':currentName,
			'verified':user.verified,
			'non_conprod':non_conprod,
			'non_accept':non_accept,
			'item_quant':item_quant,
			'messages':'The product is approved',
			'all_products':all_products,
			'data2':data2,
			'rejprod':rejprod,
			'data3':data3,
			'prodnew':prodnew

			}
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message=message)
			accounts.save()
			return render(request,'products/approveproduct.html',context)

	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')

#viewing your own product.
def myproduct(request):
	admin=False
	non_admin=False
	dealing_admin=False
	try:

		if request.session['email']:
				admin=False
				non_admin=False
				dealing_admin=False
				all_products=productlist.objects.all().order_by("product_name")
				user=useraccounts.objects.get(email=request.session['email'])
				currentName = user.first_name+" "+user.last_name
				if user.user_type == 'Admin':
						admin = True
				elif user.user_type == 'Dealing-Admin':
					dealing_admin = True

				else:
					non_admin=True
				all_products=productlog.objects.filter(status='pending').filter(email=request.session['email'])
				rejprod=productlog.objects.filter(status='denied').filter(email=request.session['email'])
				non_conprod=nonconsumable_productlog.objects.filter(issued_to=request.session['email']).filter(return_status='false').filter(product_accepted='true')
				non_accept=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='false').filter(issued_to=request.session['email'])
				ncproduct=nonconsumable_productlog.objects.filter(issued_to=request.session['email']).filter(return_status='true')
				data2=productlog.objects.filter(status='approved').filter(email=request.session['email']).union(productlog.objects.filter(status='partially approved').filter(email=request.session['email']))
				prodnew=productlist.objects.all().order_by("product_name")
				context={
				'dealing_admin':dealing_admin,
				'admin':admin,
				'non_admin':non_admin,
				'non_accept':non_accept,
				'rejprod':rejprod,
				'name':currentName,
				'non_conprod':non_conprod,
				'verified':user.verified,
				'ncproduct':ncproduct,
				'all_products':all_products,
				'data2':data2,
				'prodnew':prodnew,
				'name':currentName
				}
				return render(request,'products/listproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')


# partially Approving the product

def partialconfirm(request,id):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,
					'name' : currentName}
				return render(request,'home/base.html',context)
			dummy=productlog.objects.get(id=id)
			product_name=dummy.product_name
			prod_data=productlist.objects.get(product_name=dummy.product_name)
			email=dummy.email
			if request.method=='GET':
				quantity=str(request.GET['quant'])
				if(int(quantity)<=0 or int(quantity)>=dummy.quantity or int(quantity)>prod_data.available_quantity):
					message="Enter the valid quantity to approve"
				else:
					message="Product "+product_name+ " "+"("+ quantity+")"+" partially approved to  "+email
					if(prod_data.product_type=="non-consumable"):
						ser_list=[]
						comp_data=nonconsumable_productlog.objects.all()
						for item in comp_data:
							ser_list.append(item.product_serial_no)
						
						for i in range(int(quantity)):
							key=''
							
							for k in range(2):
								key+=random.choice(string.ascii_uppercase)
								
							for j in range(2):
								key+=random.choice(string.digits)
								
							for l in range(2):
								key+=random.choice(string.ascii_uppercase)
							
							while(True):
								if key in ser_list:
									key=''
									for k in range(0,2):
										key+=random.choice(string.ascii_uppercase)
									for j in range(0,2):
										key+=random.choice(string.digits)
									for l in range(0,2):
										key+=random.choice(string.ascii_uppercase)
								else:
									adding=nonconsumable_productlog(product_name=dummy.product_name,issued_to=email,issued_by=request.session['email'],units=1,issue_date=datetime.datetime.now(tz=timezone.utc),return_status='false',requested_quantity=1,return_request='false',product_serial_no=key,product_accepted='false')
									adding.save()
									ser_list.append(key)
									break
					productlog.objects.filter(id=id).update(status='partially approved',timestamp=datetime.datetime.now(tz=timezone.utc),approved_quantity=quantity,issued_by=request.session['email'])
					prod=productlist.objects.get(product_name=product_name)
					sizes=prod.available_quantity
					productlist.objects.filter(product_name=product_name).update(available_quantity=sizes-int(quantity))
					element=product_operationlogs.objects.filter(product_name=dummy.product_name).order_by('timestamp').last()
					value=element.final_quantity - int(quantity)
					content= product_operationlogs(product_name=dummy.product_name,timestamp=datetime.datetime.now(tz=timezone.utc),operation="subtraction",quantity=int(quantity),initial_quantity=int(element.final_quantity),final_quantity=value,issued_by=email)
					content.save()

			rejprod=productlog.objects.filter(status='denied')
			all_products=productlog.objects.filter(status='pending')
			prodnew=productlist.objects.all().order_by("product_name")
			data2=productlog.objects.filter(status='approved').union(productlog.objects.filter(status='partially approved'))
			data3=nonconsumable_productlog.objects.filter(return_status='true')
			non_conprod=nonconsumable_productlog.objects.filter(issued_to=request.session['email']).filter(return_status='false').filter(product_accepted='true')
			non_accept=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='false')
			item_quant={}
			for data in prodnew:
				sum=0
				content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
				for con in content:
					sum=sum+con.quantity
				if sum==0:
					continue
				else:
					item_quant[data.product_name]=int(sum)

			context={
			'dealing_admin':dealing_admin,
			'admin':admin,
			'rejprod':rejprod,
			'non_conprod':non_conprod,
			'non_admin':non_admin,
			'name':currentName,
			'non_accept':non_accept,
			'item_quant':item_quant,
			'data3':data3,
			'verified':user.verified,
			'messages':message,
			'all_products':all_products,
			'data2':data2,
			'prodnew':prodnew
			}
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message=message)
			accounts.save()
			return render(request,'products/approveproduct.html',context)

	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

# rejecting product request
def rejectproduct(request,id):
	admin=False
	non_admin=False
	dealing_admin=False
	logoutStatus=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
			else:
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,

					'name' : currentName}
				return render(request,'home/base.html',context)
			dummy=productlog.objects.get(id=id)
			product_name=dummy.product_name
			proddata=productlist.objects.get(product_name=dummy.product_name)
			quantity=int(dummy.quantity)
			productlog.objects.filter(id=id).update(status='denied',timestamp=datetime.datetime.now(tz=timezone.utc),approved_quantity=0)
			all_products=productlog.objects.filter(status='pending')
			rejprod=productlog.objects.filter(status='denied')
			prodnew=productlist.objects.all().order_by("product_name")
			data2=productlog.objects.filter(status='approved').union(productlog.objects.filter(status='partially approved'))
			data3=nonconsumable_productlog.objects.filter(return_status='true')
			non_conprod=nonconsumable_productlog.objects.filter(issued_to=request.session['email']).filter(return_status='false').filter(product_accepted='true')
			non_accept=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='false')
			item_quant={}
			for data in prodnew:
				sum=0
				content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
				for con in content:
					sum=sum+con.quantity
				if sum==0:
					continue
				else:
					item_quant[data.product_name]=int(sum)

			context={
			'dealing_admin':dealing_admin,
			'rejprod' : rejprod,
			'admin':admin,
			'non_admin':non_admin,
			'name':currentName,
			'verified':user.verified,
			'item_quant':item_quant,
			'messages':'The product is Rejected',
			'all_products':all_products,
			'data2':data2,
			'non_conprod':non_conprod,
			'non_accept':non_accept,
			'data3':data3,
			'prodnew':prodnew
			}
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message='request for '+product_name+' is denied')
			accounts.save()
			return render(request,'products/approveproduct.html',context)

	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':logoutStatus
		}
			return redirect('login')

# Redirecting to product approval page to check pending requests.
def pendingprods(request):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
				admin=False
				non_admin=False
				dealing_admin=False
				all_products=productlist.objects.all().order_by("product_name")
				user=useraccounts.objects.get(email=request.session['email'])
				currentName = user.first_name+" "+user.last_name
				if user.user_type == 'Admin':
						admin = True
				elif user.user_type == 'Dealing-Admin':
					dealing_admin = True
				else:
					non_admin=True
				all_products=productlog.objects.filter(status='pending').filter(email=request.session['email'])
				context={
				'dealing_admin':dealing_admin,
				'admin':admin,
				'non_admin':non_admin,
				'name':currentName,
				'verified':user.verified,
				'all_products':all_products,
				'name':currentName

				}
				return render(request,'products/canceltransaction.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

#cancel product Transaction
def canceltransaction(request,id):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
				
			else:
				non_admin=True
			dummy=productlog.objects.get(id=id)
			names=dummy.product_name
			productlog.objects.filter(id=id).filter(status='pending').delete()
			all_products=productlog.objects.filter(status='pending')
			context={
			'dealing_admin':dealing_admin,
			'admin':admin,
			'non_admin':non_admin,
			'name':currentName,
			'verified':user.verified,
			'messages':'The Transaction is cancelled',
			'all_products':all_products
			}
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message="cancelled transaction for " + names)
			accounts.save()
			return render(request,'products/canceltransaction.html',context)

	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

# redirecting to return product page
def returnproduct(request):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Non-Admin':
				non_admin = True
			else:
				dealing_admin = True
			logoutStatus=False
			productdata=nonconsumable_productlog.objects.filter(return_status='false').filter(issued_to=request.session['email']).filter(return_request='false').filter(product_accepted='true')
			context={
			'admin':admin,
			'non_admin':non_admin,
			'dealing_admin':dealing_admin,
			'all_products':all_products,
			'verified':user.verified,
			'productdata':productdata,
			'name':currentName,
			'logoutStatus':False
				}

			return render(request,'products/returnproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

# confirm the product return
def returnconfirm(request,id):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Non-Admin':
				non_admin = True
			else:
				dealing_admin = True
			logoutStatus=False
			currtime=datetime.datetime.now(tz=timezone.utc)
			all_data=nonconsumable_productlog.objects.filter(id=id).first()
			nonconsumable_productlog.objects.filter(id=id).update(return_date=currtime,return_status='false',return_request='true')
			productdata=nonconsumable_productlog.objects.filter(return_status='false').filter(return_request='false').filter(issued_to=request.session['email']).filter(product_accepted='true')
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			message="Product " + all_data.product_name+" return requested by "+request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message="Product " + all_data.product_name+" return requested by "+request.session['email'])
			accounts.save()
			context={
			'admin':admin,
			'non_admin':non_admin,
			'dealing_admin':dealing_admin,
			'all_products':all_products,
			'verified':user.verified,
			'productdata':productdata,
			'messages':message,
			'name':currentName,
			'logoutStatus':False
				}

			return render(request,'products/returnproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

#rendering the  page with non-consumable accepted products with return request.
def returnrequest(request):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			
			logoutStatus=False
			productdata=nonconsumable_productlog.objects.filter(return_status='false').filter(return_request='true').filter(product_accepted='true')
			context={
			'admin':admin,
			'non_admin':non_admin,
			'dealing_admin':dealing_admin,
			'all_products':all_products,
			'verified':user.verified,
			'productdata':productdata,
			'name':currentName,
			'logoutStatus':False
				}
			return render(request,'products/returnrequest.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

# confirming the return request for particular product
def returnrequestconfirm(request,id):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			all_products=productlist.objects.all().order_by("product_name")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			elif user.user_type == 'Non-Admin':
				non_admin = True
			else:
				dealing_admin = True
			logoutStatus=False
			currtime=datetime.datetime.now(tz=timezone.utc)
			dummy=nonconsumable_productlog.objects.get(id=id)
			nonconsumable_productlog.objects.filter(id=id).update(return_date=currtime,return_status='true')
			productdata=nonconsumable_productlog.objects.filter(return_status='false').filter(return_request='true')
			message="Product " + dummy.product_name+" return accepted by "+request.session['email']
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message="Product " + dummy.product_name+" return accepted by "+request.session['email'])
			accounts.save()
			context={
			'admin':admin,
			'non_admin':non_admin,
			'dealing_admin':dealing_admin,
			'all_products':all_products,
			'verified':user.verified,
			'productdata':productdata,
			'messages':message,
			'name':currentName,
			'logoutStatus':False
				}

			return render(request,'products/returnrequest.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')


# rendering the measurement unit / category page.
def proddb(request):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			measuredata=master_units.objects.all().order_by("measure_unit")
			categorydata=master_category.objects.all().order_by("product_category")
			measurement=set()
			categories=set()
			nondel_measure=set()
			nondel_category=set()
			for data in all_products:
				content=productlog.objects.filter(product_name=data.product_name)
				if content:
					nondel_category.add(data.product_category)
					nondel_measure.add(data.measure_unit)

			for data in measuredata:
				if data.measure_unit not in nondel_measure:
					measurement.add(data.measure_unit)

			for data in categorydata:
				if data.product_category not in nondel_category:
					categories.add(data.product_category)
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
				admin = True
			else:
				if user.user_type=='Dealing-Admin':
					dealing_admin=True
				else:
					non_admin=True
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin':dealing_admin,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,
					'messages':'Access Not Allowed',
					'name' : currentName
					}
				return redirect('home')

			context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin':dealing_admin,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,
					'nondel_category':nondel_category,
					'nondel_measure':nondel_measure,
					'categories':categories,
					'measurement':measurement,
					'name' : currentName}
			
			return render(request,'products/edit_unit_category.html',context)
		else:
			print('')
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

#adding measurement unit
def add_measure(request):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			measuredata=master_units.objects.all().order_by("measure_unit")
			categorydata=master_category.objects.all().order_by("product_category")
			measurement=set()
			categories=set()
			nondel_measure=set()
			nondel_category=set()
			for data in all_products:
				content=productlog.objects.filter(product_name=data.product_name)
				if content:
					nondel_category.add(data.product_category)
					nondel_measure.add(data.measure_unit)

			for data in measuredata:
				if data.measure_unit not in nondel_measure:
					measurement.add(data.measure_unit)

			for data in categorydata:
				if data.product_category not in nondel_category:
					categories.add(data.product_category)

			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			else:
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin':dealing_admin,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,

					'name' : currentName}
				return render(request,'home/base.html',context)

			if request.method=='POST':
				names=request.POST.get('measure')
				try:
					if master_units.objects.get(measure_unit=names):
						context={
					    'logoutStatus' : False,
					    'admin' : admin,
						'non_admin' : non_admin,
						'message':'Measure unit exists',
						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'dealing_admin' : dealing_admin,
						'nondel_measure':nondel_measure,
						'nondel_category':nondel_category,
						'categories':categories,
						'measurement':measurement,
						'name' : currentName
						}
						return render(request,'products/edit_unit_category.html',context)
				except:
					data=master_units(measure_unit=names)
					data.save()
					measurement.add(names)
					context={
					    'logoutStatus' : False,
					    'admin' : admin,
						'non_admin' : non_admin,
						'message':'Measure unit added',
						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'dealing_admin' : dealing_admin,
						'nondel_category':nondel_category,
						'nondel_measure':nondel_measure,
						'categories':categories,
						'measurement':measurement,
						'name' : currentName}
					now = datetime.datetime.now(tz=timezone.utc)
					accounts = product_transaction_logs(email =request.session['email'],timestamp = now,message="Measure unit " + names+" added by "+request.session['email'])
					accounts.save()
					return render(request,'products/edit_unit_category.html',context)
			else:
				context={
					    'logoutStatus' : False,
					    'admin' : admin,
						'non_admin' : non_admin,

						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'nondel_measure':nondel_measure,
						'nondel_category':nondel_category,
						'categories':categories,
						'dealing_admin' : dealing_admin,
						'measurement':measurement,
						'name' : currentName}
				return render(request,'products/edit_unit_category.html',context)


	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

#adding the category
def add_category(request):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			measuredata=master_units.objects.all().order_by("measure_unit")
			categorydata=master_category.objects.all().order_by("product_category")
			measurement=set()
			categories=set()
			nondel_measure=set()
			nondel_category=set()
			for data in all_products:
				content=productlog.objects.filter(product_name=data.product_name)
				if content:
					nondel_category.add(data.product_category)
					nondel_measure.add(data.measure_unit)

			for data in measuredata:
				if data.measure_unit not in nondel_measure:
					measurement.add(data.measure_unit)

			for data in categorydata:
				if data.product_category not in nondel_category:
					categories.add(data.product_category)

			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
					admin = True
			else:
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin':dealing_admin,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,

					'name' : currentName}
				return render(request,'home/base.html',context)
			if request.method=='POST':
				names=request.POST.get('category')
				try:
					if master_category.objects.get(product_category=names):
						context={
					    'logoutStatus' : False,
					    'admin' : admin,
						'non_admin' : non_admin,
						'message':'Category Already exists',
						'categories':categories,
						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'dealing_admin' : dealing_admin,
						'measurement':measurement,
						'nondel_category':nondel_category,
						'nondel_measure':nondel_measure,
						'name' : currentName}
						return render(request,'products/edit_unit_category.html',context)
				except:
					data=master_category(product_category=names)
					data.save()
					categories.add(names)
					context={
					    'logoutStatus' : False,
					    'admin' : admin,
						'non_admin' : non_admin,
						'message':'Category added successfully',
						'categories':categories,
						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'nondel_measure':nondel_measure,
						'nondel_category':nondel_category,
						'dealing_admin' : dealing_admin,
						'measurement':measurement,
						'name' : currentName}
					now = datetime.datetime.now(tz=timezone.utc)
					accounts = product_transaction_logs(email =request.session['email'],timestamp = now,message="Product Category " + names+" added by "+request.session['email'])
					accounts.save()
					return render(request,'products/edit_unit_category.html',context)
			else:

				context={
					    'logoutStatus' : False,
					    'admin' : admin,
						'non_admin' : non_admin,
						'nondel_category':nondel_category,
						'nondel_measure':nondel_measure,
						'categories':categories,
						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'dealing_admin' : dealing_admin,
						'measurement':measurement,
						'name' : currentName
						}
				return render(request,'products/edit_unit_category.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

# deleting the measure unit
def del_unit(request,name):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			measuredata=master_units.objects.all().order_by("measure_unit")
			categorydata=master_category.objects.all().order_by("product_category")
			measurement=set()
			categories=set()
			nondel_measure=set()
			nondel_category=set()
			for data in all_products:
				content=productlog.objects.filter(product_name=data.product_name)
				if content:
					nondel_category.add(data.product_category)
					nondel_measure.add(data.measure_unit)

			for data in measuredata:
				if data.measure_unit not in nondel_measure:
					measurement.add(data.measure_unit)

			for data in categorydata:
				if data.product_category not in nondel_category:
					categories.add(data.product_category)

			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
				admin = True
			else:
				if user.user_type=='Dealing-Admin':
					dealing_admin=True
				else:
					non_admin=True
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin':dealing_admin,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,

					'name' : currentName
					}
				return redirect('home')
			if name not in nondel_measure:
				master_units.objects.filter(measure_unit=name).delete()
				measurement.discard(name)
				message='measure_unit deleted successfully'
				now = datetime.datetime.now(tz=timezone.utc)
				accounts = product_transaction_logs(email =request.session['email'],timestamp = now,message="Measure unit " + name+" removed by "+request.session['email'])
				accounts.save()
			else:
				message="Measure unit is being used cannot be deleted"
			context={
					  'logoutStatus' : False,
					   'admin' : admin,
						'non_admin' : non_admin,
						'message':message,
						'nondel_measure':nondel_measure,
						'nondel_category':nondel_category,
						'categories':categories,
						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'measurement':measurement,
						'name' : currentName
						}
			
			
			return render(request,'products/edit_unit_category.html',context)
		else:
			print("")
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

# deleting particular category
def del_category(request,name):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
			measuredata=master_units.objects.all().order_by("measure_unit")
			categorydata=master_category.objects.all().order_by("product_category")
			measurement=set()
			categories=set()
			nondel_measure=set()
			nondel_category=set()
			for data in all_products:
				content=productlog.objects.filter(product_name=data.product_name)
				if content:
					nondel_category.add(data.product_category)
					nondel_measure.add(data.measure_unit)

			for data in measuredata:
				if data.measure_unit not in nondel_measure:
					measurement.add(data.measure_unit)

			for data in categorydata:
				if data.product_category not in nondel_category:
					categories.add(data.product_category)

			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			if user.user_type == 'Admin':
				admin = True

			else:
				if user.user_type=='Dealing_admin':
					dealing_admin=True
				else:
					non_admin=True
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : non_admin,
					'message' :'Not Allowed',
					'verified':user.verified,
					'dealing_admin' : dealing_admin,

					'name' : currentName}
				return redirect('home')
			if name not in nondel_category:
				master_category.objects.filter(product_category=name).delete()
				categories.discard(name)
				message='Product Category deleted successfully'
				now = datetime.datetime.now(tz=timezone.utc)
				accounts = product_transaction_logs(email =request.session['email'],timestamp = now,message="Category " + name+" removed by "+request.session['email'])
				accounts.save()
			else:
				message='Product Category is bieng used cannot be deleted'
			context={
					  'logoutStatus' : False,
					   'admin' : admin,
						'non_admin' : non_admin,
						'message':message,
						'nondel_category':nondel_category,
						'nondel_measure':nondel_measure,
						'categories':categories,
						'dealing_admin':dealing_admin,
						'verified':user.verified,
						'dealing_admin' : dealing_admin,
						'measurement':measurement,
						'name' : currentName
						}
			
			return render(request,'products/edit_unit_category.html',context)

		else:
			print("")

	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')



#rendering the accepted non-consumable products page
def accept_route(request):
	
	admin=False
	non_admin=False
	dealing_admin=False
	try:

		if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				currentName = user.first_name+" "+user.last_name
				if user.user_type == 'Admin':
						admin = True
				elif user.user_type == 'Dealing-Admin':
					dealing_admin = True

				else:
					non_admin=True
				non_accept=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='false').filter(issued_to=request.session['email'])
				context={
				'dealing_admin':dealing_admin,
				'admin':admin,
				'non_admin':non_admin,
				'non_accept':non_accept,
				'name':currentName,
				'verified':user.verified,
				}
				return render(request,'products/product_accepted.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')

#accepting the non-consumable product by user
def product_accept(request,id):
	admin=False
	non_admin=False
	dealing_admin=False
	try:
		if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				currentName = user.first_name+" "+user.last_name
				if user.user_type == 'Admin':
						admin = True
				elif user.user_type == 'Dealing-Admin':
					dealing_admin = True
				else:
					non_admin=True
				if request.method=='GET':
					data=request.GET['serial']
					content=nonconsumable_productlog.objects.filter(id=id).first()
					if data==content.product_serial_no:
						messages="product "+content.product_name+"(" +data + ")"+"accepted by "+request.session['email']
						nonconsumable_productlog.objects.filter(id=id).update(product_accepted='true')
						now = datetime.datetime.now(tz=timezone.utc)
						accounts = product_transaction_logs(email =request.session['email'],timestamp = now,message=messages)
						accounts.save()
					else:
						messages="please enter the right serial no."
				all_products=productlog.objects.filter(status='pending').filter(email=request.session['email'])
				rejprod=productlog.objects.filter(status='denied').filter(email=request.session['email'])
				non_conprod=nonconsumable_productlog.objects.filter(issued_to=request.session['email']).filter(return_status='false').filter(product_accepted='true')
				non_accept=nonconsumable_productlog.objects.filter(return_status='false').filter(product_accepted='false').filter(issued_to=request.session['email'])
				ncproduct=nonconsumable_productlog.objects.filter(issued_to=request.session['email']).filter(return_status='true')
				data2=productlog.objects.filter(status='approved').filter(email=request.session['email']).union(productlog.objects.filter(status='partially approved').filter(email=request.session['email']))
				prodnew=productlist.objects.all().order_by("product_name")
				context={
				'dealing_admin':dealing_admin,
				'admin':admin,
				'non_admin':non_admin,
				'non_accept':non_accept,
				'rejprod':rejprod,
				'name':currentName,
				'non_conprod':non_conprod,
				'verified':user.verified,
				'ncproduct':ncproduct,
				'all_products':all_products,
				'data2':data2,
				'prodnew':prodnew,
				'messages':messages,
				'name':currentName
				}
				return render(request,'products/listproduct.html',context)
	except:
		try:
			if request.session['email']:
				user=useraccounts.objects.get(email=request.session['email'])
				if user.user_type=='Admin':
					admin=True
				elif user.user_type=='Dealing-Admin':
					dealing_admin=True
				else :
					non_admin=True
				message='something went wrong'
				context={
				'admin':admin,
				'dealing_admin':dealing_admin,
				'non_admin':non_admin,
				'verified':user.verified,
				'message':message,
				'logoutStatus':False
			}
				return redirect('home')
		except:
			message = "login first"
			context = {
			'messages' : message,
			'logoutStatus':True
		}
			return redirect('login')
