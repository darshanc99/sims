from django.shortcuts import render,redirect
from .models import productlist,productlog,nonconsumable_productlog,master_units,master_category
from authentication.models import useraccounts
from logs.models import sessionlogs,product_transaction_logs
from simchat.models import simmessage
from django.utils import timezone
import datetime
import hashlib
# Create your views here.
def addproduct(request):
	logoutStatus= True
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
				print("fngfifdfjbnfg")
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
				
				
				try:
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
					
					prod.save()
					print("hererer")
					all_products=productlist.objects.all().order_by("product_name")
					messages="Product added successfully"
					currentEmail = request.session['email']
					currentUser = useraccounts.objects.get(email=currentEmail)
					currentName = currentUser.first_name+" "+currentUser.last_name
					context = {
						'admin':True,
						'dealing_admin':False,
						'non_admin':False,
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

					return render(request,'products/addproduct.html',context)		
			else:
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
		message = "you need to login first"
		context = {
			'message' : message,
			'logoutStatus':logoutStatus
		}
		return render(request,'authentication/login.html',context)					

def addquantity(request):
	logoutStatus=True
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
				print("fngfifdfjbnfg")
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
				return render(request,'products/addquantity.html',context)
			else:
				all_products=productlist.objects.all().order_by("product_name")
				
				
				context = {
					'admin':admin,
					'dealing_admin':dealing_admin,
					'non_admin':non_admin,
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
			
			admin=False
			non_admin=False
			dealing_admin=False
			all_products=productlist.objects.all().order_by("product_name")
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
				print("fngfifdfjbnfg")
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
				print("herenow")
				names=request.POST.get('product_list')
				
				password=request.POST.get('pass')
				print("here")
				password = hashlib.sha256(password.encode()).hexdigest()
				print("herethere")
				if useraccounts.objects.get(email=request.session['email']):
						
						print("yahoo")
						
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

							return render(request,'products/removeproduct.html',context)

						else:
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
		message='you need to login first'
			
		context={
				
		'message':message,
		'logoutStatus':logoutStatus
			}
		return render(request,'authentication/login.html',context)


def viewproduct(request):
	logoutStatus=True
	if request.session['email']:
		user=useraccounts.objects.get(email=request.session['email'])
		all_products=productlist.objects.filter(product_type="consumable").order_by("product_name")
		noncon_product=productlist.objects.filter(product_type="non-consumable").order_by("product_name")
		currentEmail = request.session['email']
		currentUser = useraccounts.objects.get(email=currentEmail)
		currentName = currentUser.first_name+" "+currentUser.last_name
		context={
			'admin':True,
			'dealing_admin':False,
			'non_admin':False,
			'verified':user.verified,
			'name':currentName,
			'all_products':all_products,
			'noncon_product':noncon_product
			}
		return render(request,'products/products.html',context)
	else:
		message='you need to login first'
			
		context={
		'admin':True,
		'dealing_admin':False,
		'non_admin':False,
		'verified':user.verified,		
		'message':message,
		'logoutStatus':logoutStatus
			}
		return render(request,'authentication/login.html',context)

def routeproduct(request):
	logoutStatus=True
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
				print("fngfifdfjbnfg")
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
				print("fhghgf")
				old_name=request.POST.get('product_list')
				print(old_name)
				product_name=request.POST.get('product_name')
				print(product_name)
				product_category=request.POST.get('product_category')
				print(product_category)
				product_type=request.POST.get('product_type')
				available_quantity=request.POST.get('avail_quantity')
				measure_unit=request.POST.get('measure_unit')
				print("fghghh222")
				try:
					if productlist.objects.get(product_name=product_name):
						print("hola amigos")
						message='Product with this name already exist'
						all_products=productlist.objects.all().order_by("product_name")
						
						context={
							'admin':admin,
							'dealing_admin':dealing_admin,
							'non_admin':non_admin,
							'message':message,
							'name':currentName,
							'verified':user.verified,
							'all_products':all_products
							}
						print("now here")	
						return render(request,'products/editproduct.html',context)
				except:
					print("even here ppls")
					if product_name=='':
						print("whereeetr")
						productlist.objects.filter(product_name=old_name).update(product_category=product_category,available_quantity=available_quantity,measure_unit=measure_unit,product_type=product_type)
						message='Product details updated not changing name'
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
					else:
						
						productlist.objects.filter(product_name=old_name).update(product_name=product_name,product_category=product_category,available_quantity=available_quantity,measure_unit=measure_unit,product_type=product_type)
						message='Product details updated with changing name'
						
						all_products=productlist.objects.filter(product_type="consumable").order_by("product_name")
						noncon_product=productlist.objects.filter(product_type="non-consumable").order_by("product_name")
						
						context={
							'admin':admin,
							'dealing_admin':dealing_admin,
							'non_admin':non_admin,
							'message':message,
							'verified':user.verified,
							'name':currentName,
							'noncon_product':noncon_product,
							'all_products':all_products
							}
						now = datetime.datetime.now(tz=timezone.utc)
						email=request.session['email']
						
						accounts = product_transaction_logs(email =email,timestamp = now,message="Product details/name changed from "+old_name +" to "+product_name)	
						accounts.save()	
						print("even here")
					return render(request,'products/products.html',context)
			else:
				print("doool")
				
	except:
		message="not working"
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
		
						
		return render(request,'products/products.html',context)

def edprod(request,name):
	logoutStatus=True
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
				print("fngfifdfjbnfg")
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
			
			print("doool")
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
		message='you need to login first'
	
			
		context={
		'logoutStatus':logoutStatus,
		'message':message,

			}
		return render(request,'authentication/login.html',context)

def requestproduct(request):
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
				print("fngfifdfjbnfg")
			else:
				dealing_admin = True
			print("grrieo")
			
			if request.method=='POST':
				print("ssaasarere")
				product_name=request.POST.get('product_category')
				quantity=request.POST.get('quantity')
				print(int(quantity))
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
					print("hersidmssdmind")
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
				print("heree")
				
				
				print("also here")
				
				
				
				print("ssosfndfnd")
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
		message='you need to login first'
	
			
		context={
		'logoutStatus':True,
		'message':message,
		
			}
		return render(request,'authentication/login.html',context)



def approveproduct(request):
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
				print("fngfifdfjbnfg")
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
			
			print("djvdhucdie")
			user=useraccounts.objects.get(email=request.session['email'])
			currentName = user.first_name+" "+user.last_name
			all_products=productlog.objects.filter(status='pending')
			prodnew=productlist.objects.all().order_by("product_name")
			item_quant={}
			for data in prodnew:
				print("sdsd")

				sum=0
				content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
				for con in content:
					print(con.quantity)
					sum=sum+con.quantity
				if sum==0:
					continue
				else:
					print(sum)
					item_quant[data.product_name]=int(sum)
			print(item_quant)		


			data2=productlog.objects.filter(status='approved')
			print(all_products)
			context={
			'dealing_admin':dealing_admin,
			'admin':admin,
			'non_admin':non_admin,
			'name':currentName,
			'verified':user.verified,
			'item_quant':item_quant,
			'all_products':all_products,
			'data2':data2,
			'prodnew':prodnew	
			}
					
			print('now')
			return render(request,'products/approveproduct.html',context)
	except:
		messages='login first'
		context = {
				'logoutStatus' : True,
					
				'message' : messages,
					
					}
		return render(request,'authentication/login.html',context)

def productconfirm(request,id,quantity):
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
				print("fngfifdfjbnfg")
			else:
				context={
					'logoutStatus' : False,
					'admin' : admin,
					'non_admin' : True,
					'verified':user.verified,
					'dealing_admin' : dealing_admin,
						
					'name' : currentName}
				return render(request,'home/base.html',context)
			print("ayaa")

			dummy=productlog.objects.get(id=id)

			print(dummy)
			product_name=dummy.product_name
			proddata=productlist.objects.get(product_name=dummy.product_name)

			email=dummy.email
			if(proddata.product_type=='non-consumable'):
				adding=nonconsumable_productlog(product_name=dummy.product_name,issued_to=email,issued_by=request.session['email'],units=quantity,issue_date=datetime.datetime.now(tz=timezone.utc),return_status='false',requested_quantity=dummy.quantity)
				adding.save()
				print("added successfully")
			message="Product "+product_name+" "+ "with quantity" +"("+quantiy+")"+ " Completely approved to  "+email
			

			productlog.objects.filter(id=id).update(status='approved',timestamp=datetime.datetime.now(tz=timezone.utc),approved_quantity=quantity)
			print("ollaa")

			all_products=productlog.objects.filter(status='pending')
			data2=productlog.objects.filter(status='approved')

			prod=productlist.objects.get(product_name=product_name)
			sizes=prod.available_quantity
			prodnew=productlist.objects.all().order_by("product_name")
			productlist.objects.filter(product_name=product_name).update(available_quantity=sizes-int(quantity))

			item_quant={}
			for data in prodnew:
				print("sdsd")

				sum=0
				content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
				for con in content:
					print(con.quantity)
					sum=sum+con.quantity
				if sum==0:
					continue
				else:
					print(sum)
					item_quant[data.product_name]=int(sum)

			print(item_quant)
			print(all_products)
			context={
			'dealing_admin':dealing_admin,
			'admin':admin,
			'non_admin':non_admin,
			'name':currentName,
			'verified':user.verified,
			'item_quant':item_quant,
			'messages':'The product is approved',
			'all_products':all_products,
			'data2':data2,
			'prodnew':prodnew
				
			}
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message=message)	
			accounts.save()
					
			print('now')
			return render(request,'products/approveproduct.html',context)

	except:
		message='you need to login first'
	
			
		context={
		'logoutStatus':logoutStatus,
		'message':message,
		
			}
		return render(request,'authentication/login.html',context)

def myproduct(request):
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
				ncproduct=nonconsumable_productlog.objects.filter(issued_to=request.session['email']).filter(return_status='true')
				data2=productlog.objects.filter(status='approved').filter(email=request.session['email'])
				prodnew=productlist.objects.all().order_by("product_name")
				print(all_products)
				context={
				'dealing_admin':dealing_admin,
				'admin':admin,
				'non_admin':non_admin,
				'name':currentName,
				'verified':user.verified,
				'ncproduct':ncproduct,
				'all_products':all_products,
				'data2':data2,
				'prodnew':prodnew,
				'name':currentName
					
				}
						
				print('now')
				return render(request,'products/listproduct.html',context)
	except:
		messages='login first'
		context = {
				'logoutStatus' : True,
					
				'message' : messages,
					
					}
		return render(request,'authentication/login.html',context)

def partialconfirm(request,id):
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
				print("fngfifdfjbnfg")
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

			print(dummy)
			product_name=dummy.product_name
			prod_data=productlist.objects.get(product_name=dummy.product_name)
			email=dummy.email
			print(prod_data)
			
			if request.method=='GET':

				
				quantity=str(request.GET['quant'])
				if(int(quantity)<=0 or int(quantity)>=dummy.quantity):
					message="Enter the valid quantity to approve"
				
				else:
					message="Product "+product_name+ " "+"("+ quantity+")"+" partially approved to  "+email
					
					if(prod_data.product_type=="non-consumable"):
						print("gerere")
						adding=nonconsumable_productlog(product_name=dummy.product_name,issued_to=email,issued_by=request.session['email'],units=quantity,issue_date=datetime.datetime.now(tz=timezone.utc),return_status='false',requested_quantity=dummy.quantity)
						adding.save()
						


					productlog.objects.filter(id=id).update(status='approved',timestamp=datetime.datetime.now(tz=timezone.utc),approved_quantity=quantity)
					prod=productlist.objects.get(product_name=product_name)
					sizes=prod.available_quantity
					productlist.objects.filter(product_name=product_name).update(available_quantity=sizes-int(quantity))
			

			all_products=productlog.objects.filter(status='pending')
			prodnew=productlist.objects.all().order_by("product_name")
			data2=productlog.objects.filter(status='approved')

			item_quant={}
			for data in prodnew:
				print("sdsd")

				sum=0
				content=productlog.objects.filter(status='pending').filter(product_name=data.product_name)
				for con in content:
					print(con.quantity)
					sum=sum+con.quantity
				if sum==0:
					continue
				else:
					print(sum)
					item_quant[data.product_name]=int(sum)
			print(item_quant)
			
			
			print(all_products)

			context={
			'dealing_admin':dealing_admin,
			'admin':admin,
			'non_admin':non_admin,
			'name':currentName,
			'item_quant':item_quant,
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
					
			print('now')
			return render(request,'products/approveproduct.html',context)

	except:
		message='you need to login first'
	
			
		context={
		'logoutStatus':True,
		'message':message,
		
			}
		return render(request,'authentication/login.html',context)


def pendingprods(request):
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
				
				print(all_products)
				context={
				'dealing_admin':dealing_admin,
				'admin':admin,
				'non_admin':non_admin,
				'name':currentName,
				'verified':user.verified,
				
				'all_products':all_products,
				
				'name':currentName
					
				}
						
				print('now')
				return render(request,'products/canceltransaction.html',context)
	except:
		messages='login first'
		context = {
				'logoutStatus' : True,
					
				'message' : messages,
					
					}
		return render(request,'authentication/login.html',context)

def canceltransaction(request,id):
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
				print("fngfifdfjbnfg")
			else:
				non_admin=True
			

			dummy=productlog.objects.get(id=id)

			names=dummy.product_name 

			print(dummy)
			
			productlog.objects.filter(id=id).filter(status='pending').delete()
			

			all_products=productlog.objects.filter(status='pending')
			

			
			print(all_products)
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
					
			print('now')
			return render(request,'products/canceltransaction.html',context)

	except:
		message='you need to login first'
	
			
		context={
		'logoutStatus':logoutStatus,
		'message':message,
		
			}
		return render(request,'authentication/login.html',context)


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
				print("fngfifdfjbnfg")
			else:
				dealing_admin = True
			print("grrieo")
			
			
			logoutStatus=False
			
			productdata=nonconsumable_productlog.objects.filter(return_status='false').filter(issued_to=request.session['email'])	
				
			print("ssosfndfnd")
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
		message = "You have been logged out. Please log in again!"
		logoutStatus = True

		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)
		
def returnconfirm(request,name,id):
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
				print("fngfifdfjbnfg")
			else:
				dealing_admin = True
			print("grrieo")
			
			
			logoutStatus=False
			currtime=datetime.datetime.now(tz=timezone.utc)

			nonconsumable_productlog.objects.filter(product_name=name).filter(id=id).update(return_date=currtime,return_status='true')
			
			productdata=nonconsumable_productlog.objects.filter(return_status='false').filter(issued_to=request.session['email'])	
				
			print("returned")
			now = datetime.datetime.now(tz=timezone.utc)
			emails=request.session['email']
			accounts = product_transaction_logs(email =emails,timestamp = now,message="Product " + name+" returned by "+request.session['email'])	
			accounts.save()
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
		message = "You have been logged out. Please log in again!"
		logoutStatus = True

		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)


def proddb(request):
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
			
			 
			print("doing great")
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
			print("nice")		
			return render(request,'products/edit_unit_category.html',context)
		else:
			print('nothing')
	except:
		message = "You have been logged out. Please log in again!"
		logoutStatus = True

		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def add_measure(request):
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
				print("fine")
				names=request.POST.get('measure')
				
				print(names)
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
						'name' : currentName}
						print("nice")		
						return render(request,'products/edit_unit_category.html',context)
				except:
					print("also herrre")
					data=master_units(measure_unit=names)
					data.save()
					print("macho")
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
					print("nice111")
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
				print("nice")		
				return render(request,'products/edit_unit_category.html',context)


	except:
		message = "You have been logged out. Please log in again!"
		logoutStatus = True
		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)


def add_category(request):
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
				print("fine")
				names=request.POST.get('category')
			
				print(names)
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
						print("nice")		
						return render(request,'products/edit_unit_category.html',context)
				except:
					print("also herrre")
					data=master_category(product_category=names)
					data.save()
					categories.add(names)
					print("macho")
					
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
					print("nice111")
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
						'name' : currentName}
				print("nice")		
				return render(request,'products/edit_unit_category.html',context)


	except:
		message = "You have been logged out. Please log in again!"
		logoutStatus = True
		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def del_unit(request,name):
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
			master_units.objects.filter(measure_unit=name).delete()
			measurement.discard(name)
			
			context={
					  'logoutStatus' : False,
					   'admin' : admin,
						'non_admin' : non_admin,
						'message':'measure_unit deleted successfully',
						'nondel_measure':nondel_measure,
						'nondel_category':nondel_category,
						'categories':categories,
						'dealing_admin':dealing_admin, 
						'verified':user.verified,
						'dealing_admin' : dealing_admin,
						'measurement':measurement,
						'name' : currentName}
			print("nice111")
			now = datetime.datetime.now(tz=timezone.utc)
			accounts = product_transaction_logs(email =request.session['email'],timestamp = now,message="Measure unit " + name+" removed by "+request.session['email'])	
			accounts.save()
			return render(request,'products/edit_unit_category.html',context)

		else:
			print("nothing")

	except:
		message = "You have been logged out. Please log in again!"
		logoutStatus = True
		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def del_category(request,name):
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

			master_category.objects.filter(product_category=name).delete()
			categories.discard(name)
			
			context={
					  'logoutStatus' : False,
					   'admin' : admin,
						'non_admin' : non_admin,
						'message':'Product Category deleted successfully',
						'nondel_category':nondel_category,
						'nondel_measure':nondel_measure,
						'categories':categories,
						'dealing_admin':dealing_admin, 
						'verified':user.verified,
						'dealing_admin' : dealing_admin,
						'measurement':measurement,
						'name' : currentName}
			print("nice111")
			now = datetime.datetime.now(tz=timezone.utc)
			accounts = product_transaction_logs(email =request.session['email'],timestamp = now,message="Category " + name+" Removed by "+request.session['email'])	
			accounts.save()		
			return render(request,'products/edit_unit_category.html',context)

		else:
			print("nothing")

	except:
		message = "You have been logged out. Please log in again!"
		logoutStatus = True
		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def pd_logs(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		if request.session['email']:
			email = request.session['email']
			user = useraccounts.objects.get(email=email)

			name=user.first_name + " " + user.last_name
			logoutStatus = False

			all_msg = simmessage.objects.all()
			msg_count = 0
			for msgs in all_msg:
				if msgs.receiver == request.session['email'] and msgs.read == False:
							msg_count+=1

			if user.user_type == 'Admin':
				admin = True
				all_logs = product_transaction_logs.objects.all().order_by('timestamp').reverse()
				verified = user.verified
				print("fdhfdh")
				context = {
							'name' : name,
							'admin' : admin,
							'non_admin' : non_admin,
							'dealing_admin' : dealing_admin,
							'logoutStatus' : logoutStatus,
							'all_logs' : all_logs,
							'msg_count' : msg_count,
							'verified' : verified
				}
				print("heredamn")
				return render(request,'products/pd_logs.html',context)
			elif user.user_type == 'Non-Admin':
				non_admin = True
				verified = user.verified
				all_logs = product_transaction_logs.objects.all().order_by('timestamp').reverse()
				my_logs = []
				for log in all_logs:
					if log.email == request.session['email']:
								my_logs.append(log)
				context = {
							'name' : name,
							'admin' : admin,
							'non_admin' : non_admin,
							'dealing_admin' : dealing_admin,
							'verified' : verified,
							'logoutStatus' : logoutStatus,
							'all_logs' : my_logs,
							'msg_count' : msg_count
				}
				return render(request,'products/pd_logs.html',context)
			elif user.user_type == 'Dealing-Admin':
				dealing_admin = True
				verified = user.verified
				all_logs = product_transaction_logs.objects.all().order_by('timestamp').reverse()
				my_logs = []
				for log in all_logs:
					if log.email == request.session['email']:
						my_logs.append(log)
				context = {
							'name' : name,
							'admin' : admin,
							'non_admin' : non_admin,
							'dealing_admin' : dealing_admin,
							'logoutStatus' : logoutStatus,
							'all_logs' : my_logs,
							'msg_count' : msg_count,
							'verified' : verified
				}
				return render(request,'products/pd_logs.html',context)
	except:
				#If user not logged in
		print("herere")		
		return redirect('login')