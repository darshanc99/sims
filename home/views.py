#Import Dependencies
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from authentication.models import useraccounts, master_user_types
from logs.models import sessionlogs, product_transaction_logs, product_operationlogs
from products.models import productlog, nonconsumable_productlog, productlist
import datetime, hashlib
from django.utils import timezone
from simchat.models import simmessage
from itertools import chain
import csv
from django.http import HttpResponse

#Write your view here
#Home Function
def home(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		#If user logged in
		if request.session['email']:
			email = request.session['email']
			user = useraccounts.objects.get(email=email)

			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			name=user.first_name + " " + user.last_name
			logoutStatus = False

			all_msg = simmessage.objects.all()
			msg_count = 0
			for msgs in all_msg:
				if msgs.receiver == request.session['email'] and msgs.read == False:
					msg_count+=1

			if user.user_type == 'Admin':
				admin = True
				all_logs = sessionlogs.objects.all().order_by('timestamp').reverse()
				product_requests = productlog.objects.all().order_by('timestamp').reverse()
				product_logs = product_transaction_logs.objects.all().order_by('timestamp').reverse()
				verified = user.verified
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'all_logs' : all_logs,
					'product_requests' : product_requests,
					'product_logs' : product_logs,
					'msg_count' : msg_count,
					'verified' : verified
				}
				return render(request,'home/home.html',context)
			elif user.user_type == 'User':
				non_admin = True
				verified = user.verified
				all_logs = sessionlogs.objects.filter(email=user.email).order_by('timestamp').reverse()
				product_requests = productlog.objects.filter(email=user.email).order_by('timestamp').reverse()
				product_logs = product_transaction_logs.objects.filter(email=user.email).order_by('timestamp').reverse()
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'verified' : verified,
					'logoutStatus' : logoutStatus,
					'all_logs' : all_logs,
					'product_requests' : product_requests,
					'product_logs' : product_logs,
					'msg_count' : msg_count
				}
				return render(request,'home/home.html',context)
			elif user.user_type == 'Dealing-Hand':
				dealing_admin = True
				verified = user.verified
				all_logs = sessionlogs.objects.filter(email=user.email).order_by('timestamp').reverse()
				product_requests = productlog.objects.filter(email=user.email).order_by('timestamp').reverse()
				product_logs = product_transaction_logs.objects.filter(email=user.email).order_by('timestamp').reverse()
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'all_logs' : all_logs,
					'product_requests' : product_requests,
					'product_logs' : product_logs,
					'msg_count' : msg_count,
					'verified' : verified
				}
				return render(request,'home/home.html',context)
	except:
		#If user not logged in
		return redirect('login')

#The Filters
def filter(request):
	admin = False
	non_admin = False
	dealing_admin = False
	try:
		#If user logged in
		if request.session['email']:
			user = useraccounts.objects.get(email=request.session['email'])
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')
			name = user.first_name + " " + user.last_name
			logoutStatus = False
			#Only if the user is a verified admin
			if user.user_type == 'Admin' and user.verified:
				admin = True
				#If there is a POST method
				if request.method == 'POST':
					email = request.POST.get('email')
					option = request.POST.get('option')
					try:
						#If user with that email exists
						if useraccounts.objects.get(email=email):
							if option == 'Session Activities':
								all_logs = sessionlogs.objects.filter(email=email).order_by('timestamp').reverse()
								context = {
									'name' : name,
									'admin' : admin,
									'dealing_admin' : dealing_admin,
									'non_admin' : non_admin,
									'verified' : True,
									'logoutStatus' : logoutStatus,
									'all_logs' : all_logs,
									'useremail' : email,
									'option' : option,
								}
								return render(request,'home/filter.html',context)
							elif option == 'Product Transactions':
								product_requests = productlog.objects.filter(email=email).order_by('timestamp').reverse()
								product_logs = product_transaction_logs.objects.filter(email=email).order_by('timestamp').reverse()
								context = {
									'name' : name,
									'admin' : admin,
									'dealing_admin' : dealing_admin,
									'non_admin' : non_admin,
									'verified' : True,
									'logoutStatus' : logoutStatus,
									'product_requests' : product_requests,
									'product_logs' : product_logs,
									'useremail' : email,
									'option' : option,
								}
								return render(request,'home/filter.html',context)
					except:
						#If user with that email does not exist
						message = 'User does not exist. Please give a valid email!'
						all_logs = sessionlogs.objects.all().order_by('timestamp').reverse()
						product_requests = productlog.objects.all().order_by('timestamp').reverse()
						product_logs = product_transaction_logs.objects.all().order_by('timestamp').reverse()
						context = {
							'name' : name,
							'admin' : admin,
							'non_admin' : non_admin,
							'dealing_admin' : dealing_admin,
							'verified' : user.verified,
							'message' : message,
							'logoutStatus' : logoutStatus,
							'all_logs' : all_logs,
							'product_requests' : product_requests,
							'product_logs' : product_logs,
						}
						return render(request,'home/home.html',context)
				else:
					return redirect('home')
			else:
				#If user is either unverified or not an admin
				return redirect('home')
	except:
		#If user logged loged out
		return redirect('login')

#Add New User
def newuser(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		#If user logged in
		if request.session['email']:
			logoutStatus = False
			#Create the user object
			currentUser = useraccounts.objects.get(email=request.session['email'])
			#If user has been logged out or freezed by the admin
			if currentUser.loginstatus == False or currentUser.accountstatus == False:
				return redirect('logout')
			name = currentUser.first_name + ' ' + currentUser.last_name

			#Add user flexibility available only to a verifed admin
			if currentUser.user_type == 'Admin' and currentUser.verified:
				admin = True
				#If POST request
				if request.method == 'POST':
					#Get the fields
					first_name = request.POST.get('first_name')
					last_name = request.POST.get('last_name')
					newname = first_name + ' ' + last_name
					email = request.POST.get('email')
					phone = request.POST.get('phone')
					user_role = request.POST.get('user_role')
					user_type = request.POST.get('user_type')
					password = request.POST.get('password')
					password = hashlib.sha256(password.encode()).hexdigest()

					#Save the new user
					now = datetime.datetime.now(tz=timezone.utc)
					verified = True
					loginstatus = False
					user = useraccounts(first_name,last_name,email,phone,user_type,password,user_role,now,verified,loginstatus)
					user.save()

					#Save the new entry to logs
					message = 'User created for '+ newname
					logoutStatus = False
					body = "Created account for "+ email
					accounts = sessionlogs(email=request.session['email'],timestamp=now,message=body)
					accounts.save()

					#Master table edits
					usertype = master_user_types.objects.get(user_type=user_type)
					usertype.deletestatus = False
					usertype.save()

					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'name' : name,
						'logoutStatus' : logoutStatus,
						'message' : message,
						'verified' : currentUser.verified
					}
					return redirect('userbase')
				else:
					#If no POST request, render the page
					all_usertypes = master_user_types.objects.all().order_by('user_type')
					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'logoutStatus' : logoutStatus,
						'name' : name,
						'verified' : currentUser.verified,
						'all_usertypes' : all_usertypes
					}
					return render(request,'home/adduser.html',context)
			else:
				#If user unverified or not an Admin, redirect to home page
				return redirect('home')
	except:
		#Error Handler
		return redirect('home')

#The Userbase
def userbase(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		#If user logged in
		if request.session['email']:
			currentUser = useraccounts.objects.get(email=request.session['email'])
			#If user has been logged out or freezed by the admin
			if currentUser.loginstatus == False or currentUser.accountstatus == False:
				return redirect('logout')
			#If user is a verified Admin
			if currentUser.user_type == 'Admin' and currentUser.verified:
				admin = True
				all_users = useraccounts.objects.all().order_by('first_name','last_name','email')
				all_usertypes = master_user_types.objects.all().order_by('user_type')
				logoutStatus = False
				name = currentUser.first_name + ' ' + currentUser.last_name
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'all_users' : all_users,
					'verified' : currentUser.verified,
					'all_usertypes' : all_usertypes,
				}
				return render(request,'home/userbase.html',context)
			else:
				#If user is unverified or not an admin
				return redirect('home')
	except:
		#Error Handler
		return redirect('home')

#Log out a user
def offline(request,email):
	try:
		#If user is logged in
		if request.session['email']:
			currentUser = useraccounts.objects.get(email=request.session['email'])
			user = useraccounts.objects.get(email=email)
			#If user has been logged out or freezed by the admin
			if currentUser.loginstatus == False or currentUser.accountstatus == False:
				return redirect('logout')
			#If user is a verified admin
			if currentUser.user_type == 'Admin' and currentUser.verified:

				#If the email is the current user's email
				if email == request.session['email']:
					return redirect('logout')
				else:
					user.loginstatus = False
					user.save()
					now = datetime.datetime.now(tz=timezone.utc)
					message = email + " logged out by " + request.session['email'] + "."
					accounts = sessionlogs(email=email,timestamp=now,message=message)
					accounts.save()
					accounts = sessionlogs(email=request.session['email'],timestamp=now,message=message)
					accounts.save()

					return redirect('userbase')
			else:
				#User is not a verified admin
				return redirect('home')
	except:
		return redirect('home')

#Verify a user
def verify(request,email):
	#If user logged in
	try:
		if request.session['email']:
			currentEmail = request.session['email']
			user = useraccounts.objects.get(email=currentEmail)
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			#Check if the user is a verified Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					user.verified = True
					user.save()
					now = datetime.datetime.now(tz=timezone.utc)
					message = "Verified for "+email
					session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
					session.save()
					return redirect('userbase')
				except:
					return redirect('home')
			else:
				#If user is an unverified or not an admin
				return redirect('home')
	except:
		#If user not logged in, redirect to login page
		return redirect('login')

#Delete an unverified user
def deleteuser(request,email):
	#If user logged in
	try:
		if request.session['email']:
			currentEmail = request.session['email']
			user = useraccounts.objects.get(email=currentEmail)
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			#Check if the user is a verifed Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					#Only if the user is unverified
					if user.verified == False:
						to = "+91"+str(user.phone)
						user.delete()
						now = datetime.datetime.now(tz=timezone.utc)
						message = email + " deleted."
						session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
						session.save()
						return redirect('userbase')
					else:
						return redirect('home')
				except:
					return redirect('home')
			else:
				#If user is an unverified or not an admin
				return redirect('home')
	except:
		#If user not logged in
		return redirect('login')

#Freeze a user
def freezeuser(request,email):
	#If user logged in
	try:
		if request.session['email']:
			currentEmail = request.session['email']
			user = useraccounts.objects.get(email=currentEmail)
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			#If user is a verified user
			if user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					user.accountstatus = False
					user.loginstatus = False
					user.save()
					now = datetime.datetime.now(tz=timezone.utc)
					message = "Account freezed for "+email
					session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
					session.save()
					return redirect('userbase')
				except:
					return redirect('home')
			else:
				#If user is an unverified or not an admin
				return redirect('home')
	except:
		#If user not logged in
		return redirect('login')

#Unfreeze a User
def unfreezeuser(request,email):
	#If user logged in
	try:
		if request.session['email']:
			user = useraccounts.objects.get(email=request.session['email'])
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			#If user is a verifed Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					user.accountstatus = True
					user.save()
					now = datetime.datetime.now(tz=timezone.utc)
					message = "Account unfreezed for "+email
					session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
					session.save()
					return redirect('userbase')
				except:
					return redirect('home')
			else:
				#If user is an unverified or not an admin
				return redirect('home')
	except:
		#If user is not logged in
		return redirect('login')

#Edit User Function
def edituser(request,email):
	logoutStatus = True
	admin = False
	non_admin = False
	dealing_admin = False
	#If user is logged in
	try:
		if request.session['email']:
			user = useraccounts.objects.get(email=request.session['email'])
			name = user.first_name + ' ' + user.last_name
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			#If user is a verifed Admin
			if user.user_type == 'Admin' and user.verified:
				admin = True
				try:
					user = useraccounts.objects.get(email=email)
					oldemail = user.email
					#If POST request
					if request.method == 'POST':
						first_name = request.POST.get('first_name')
						last_name = request.POST.get('last_name')
						email = request.POST.get('email')
						phone = request.POST.get('phone')
						user_type = request.POST.get('user_type')
						userrole = request.POST.get('user_role')
						user.first_name = first_name
						user.last_name = last_name
						user.email = email
						user.phone = phone
						user.user_type = user_type
						user.userrole = userrole
						user.save()

						type = master_user_types.objects.get(user_type=user_type)
						type.deletestatus = False
						type.save()

						logoutStatus = False
						all_usertypes = master_user_types.objects.all().order_by('user_type')
						context = {
							'name' : name,
							'logoutStatus' : logoutStatus,
							'admin' : admin,
							'user' : user,
							'verified' : user.verified,
							'dealing_admin' : dealing_admin,
							'non_admin' : non_admin,
							'all_usertypes' : all_usertypes,
						}
						now = datetime.datetime.now(tz=timezone.utc)
						message = "Account edited for "+email
						session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
						session.save()
						return render(request,'home/edituser.html',context)
					else:
						#If no POST request
						all_usertypes = master_user_types.objects.all().order_by('user_type')
						logoutStatus = False
						admin = True
						context = {
							'name' : name,
							'logoutStatus' : logoutStatus,
							'admin' : admin,
							'user' : user,
							'verified' : user.verified,
							'non_admin' : non_admin,
							'dealing_admin' : dealing_admin,
							'all_usertypes' : all_usertypes,
						}
						return render(request,'home/edituser.html',context)
				except:
					return redirect('home')
			else:
				#If user is an unverified or not an admin
				return redirect('home')
	except:
		#If not logged in
		return redirect('login')

#Edit User Password
def edituserpassword(request,email):
	print("Editing",email,"password.")
	logoutStatus = True
	admin, dealing_admin, non_admin = False, False, False
	try:
		if request.session['email']:
			logoutStatus = False
			currentUser = useraccounts.objects.get(email=request.session['email'])
			if currentUser.user_type == 'Admin':
				admin = True
			elif currentUser.user_type == 'Dealing-Hand':
				dealing_admin = True
			else:
				non_admin = True
			try:
				#Reset Password POST Method
				if request.method == 'POST':
					newpassword = request.POST.get('newpassword')
					newpassword = hashlib.sha256(newpassword.encode()).hexdigest()
					yourpassword = request.POST.get('yourpassword')
					yourpassword = hashlib.sha256(yourpassword.encode()).hexdigest()
					currentUser = useraccounts.objects.get(email = request.session['email'])
					if currentUser.userpassword == yourpassword and currentUser.user_type == 'Admin' and currentUser.verified:
						user = useraccounts.objects.get(email=email)
						user.userpassword = newpassword
						user.save()
						message = "Password Reset Successful."
						all_usertypes = master_user_types.objects.all().order_by('user_type')
						name = currentUser.first_name + ' ' + currentUser.last_name
						context = {
							'name' : name,
							'logoutStatus' : logoutStatus,
							'admin' : admin,
							'user' : currentUser,
							'verified' : currentUser.verified,
							'dealing_admin' : dealing_admin,
							'non_admin' : non_admin,
							'all_usertypes' : all_usertypes,
							'message' : message,
						}
						now = datetime.datetime.now(tz=timezone.utc)
						message = "Password updated for "+email
						session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
						session.save()
						return render(request,'home/edituser.html',context)
			except:
				return redirect('userbase')
	except:
		return redirect('home')

#Delete user type
def deleteusertype(request,usertype):
	#If logged in
	try:
		if request.session['email']:
			user = useraccounts.objects.get(email=request.session['email'])
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			#If user is a verified Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					type = master_user_types.objects.get(user_type=usertype)
					#If deletable
					if type.deletestatus:
						type.delete()
						message = "Removed " + usertype + " from the master_user_types."
						now = datetime.datetime.now(tz=timezone.utc)
						session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
						session.save()
						return redirect('userbase')
					else:
						#else return to the userbase
						return redirect('userbase')
				except:
					return redirect('home')
			else:
				#If user is an unverified or not an admin
				return redirect('home')
	except:
		#If not logged in
		return redirect('login')

#Add new user type
def newusertype(request):
	try:
		#If user is logged in
		if request.session['email']:
			currentUser = useraccounts.objects.get(email=request.session['email'])
			#If user has been logged out or freezed by the admin
			if currentUser.loginstatus == False or currentUser.accountstatus == False:
				return redirect('logout')

			#If user is a verified Admin
			if currentUser.user_type == 'Admin' and currentUser.verified:
				admin = True
				#If POST method
				if request.method == 'POST':
					usertype = request.POST.get('usertype')
					#Some string handlers, to get the string in the format: (Xy-Ab)
					usertype = usertype.strip()
					usertype = usertype.title()
					usertype = ' '.join(usertype.split())
					usertype = usertype.replace(' ','-')
					type = master_user_types(user_type=usertype)
					type.save()
					now = datetime.datetime.now(tz=timezone.utc)
					message = "Added " + usertype + " in master_user_types."
					accounts = sessionlogs(email=currentUser.email,timestamp=now,message=message)
					accounts.save()
					return redirect('userbase')
				else:
					#If no POST method
					return redirect('userbase')
			else:
				#If user is an unverified or not an admin
				return redirect('home')
	except:
		#If user not logged in
		return redirect('login')

#Error404 Handler
def error(request):
	logoutStatus = True
	context = {
		'logoutStatus' : logoutStatus
	}
	return render(request,'home/error.html',context)

#Report Function
def report(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		#If user is already logged in
		if request.session['email']:
			email = request.session['email']
			user = useraccounts.objects.get(email=email)
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			name = user.first_name + ' ' + user.last_name
			logoutStatus = False

			#If user is a verified admin
			if user.user_type == 'Admin' and user.verified:
				admin = True
				#If POST method
				if request.method == 'POST':
					start_date = request.POST.get('start_date')
					end_date = request.POST.get('end_date')

					#date = end_date + 1
					date = end_date
					date = date.strip()
					date = date.split('-')
					date = datetime.date(int(date[0]),int(date[1]),int(date[2]))
					date+=datetime.timedelta(days=1)
					date = str(date)

					if end_date >= start_date:
						result = []
						#get all the products
						products = productlist.objects.filter(arrival_date__lte=date).order_by('product_name')
						for product in products:
							temp = {}
							temp['product'] = product.product_name
							temp['category'] = product.product_category
							query = product_operationlogs.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date))
							#Check if query is None
							if len(query) == 0:
								query = product_operationlogs.objects.filter(product_name=product.product_name).order_by('timestamp').reverse()
								temp['opening_balance'] = query[0].final_quantity
								temp['closing_balance'] = temp['opening_balance']
								temp['net'] = abs(temp['closing_balance']-temp['opening_balance'])
								total_requests = productlog.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).values_list('quantity', flat=True)
								total_requests = sum(total_requests)
								total_approved = productlog.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).values_list('approved_quantity', flat=True)
								total_approved = sum(total_approved)
								temp['requests'] = total_requests
								temp['approved'] = total_approved
								if total_requests > 0:
									temp['approvedcent'] = round(total_approved*100/total_requests,2)
								else:
									temp['approvedcent'] = '-'
							else:
								temp['opening_balance'] = query[0].initial_quantity
								query = product_operationlogs.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).order_by('timestamp')
								count,c = len(query),0
								for q in query:
									c+=1
									if c == count:
										temp['closing_balance'] = q.final_quantity
								temp['net'] = abs(temp['closing_balance']-temp['opening_balance'])
								total_requests = productlog.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).values_list('quantity', flat=True)
								total_requests = sum(total_requests)
								total_approved = productlog.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).values_list('approved_quantity', flat=True)
								total_approved = sum(total_approved)
								temp['requests'] = total_requests
								temp['approved'] = total_approved
								if total_requests > 0:
									temp['approvedcent'] = round(total_approved*100/total_requests,2)
								else:
									temp['approvedcent'] = '-'
							result.append(temp)

						message = 'Currently, showing report for <b>' + start_date + "</b> - <b>" + end_date + "</b>."
						context = {
							'admin' : admin,
							'non_admin' : non_admin,
							'dealing_admin' : dealing_admin,
							'verified' : user.verified,
							'name' : name,
							'text' : message,
							'result' : result,
							'start' : start_date,
							"end" : end_date,
						}
						return render(request,'home/report.html',context)
					else:
						message = 'Error: End Date was found smaller than the Start Date! Please try again with smaller Start Date.'
						result = []
						products = productlist.objects.all().order_by('product_name')
						for product in products:
							temp = {}
							temp['product'] = product.product_name
							temp['category'] = product.product_category
							query = product_operationlogs.objects.filter(product_name=product.product_name)
							temp['opening_balance'] = query[0].initial_quantity
							query = product_operationlogs.objects.filter(product_name=product.product_name).order_by('timestamp').reverse()
							temp['closing_balance'] = query[0].final_quantity
							temp['net'] = abs(temp['closing_balance']-temp['opening_balance'])
							total_requests = productlog.objects.filter(product_name=product.product_name).values_list('quantity', flat=True)
							total_requests = sum(total_requests)
							total_approved = productlog.objects.filter(product_name=product.product_name).values_list('approved_quantity', flat=True)
							total_approved = sum(total_approved)
							temp['requests'] = total_requests
							temp['approved'] = total_approved
							if total_requests > 0:
								temp['approvedcent'] = round(total_approved*100/total_requests,2)
							else:
								temp['approvedcent'] = '-'
							result.append(temp)
						context = {
							'admin' : admin,
							'non_admin' : non_admin,
							'dealing_admin' : dealing_admin,
							'verified' : user.verified,
							'name' : name,
							'message' : message,
							'result' : result,
						}
						return render(request,'home/report.html',context)
				else:
					#If no POST method
					result = []
					products = productlist.objects.all().order_by('product_name')
					for product in products:
						temp = {}
						temp['product'] = product.product_name
						temp['category'] = product.product_category
						query = product_operationlogs.objects.filter(product_name=product.product_name)
						temp['opening_balance'] = query[0].initial_quantity
						query = product_operationlogs.objects.filter(product_name=product.product_name).order_by('timestamp').reverse()
						temp['closing_balance'] = query[0].final_quantity
						temp['net'] = abs(temp['closing_balance']-temp['opening_balance'])
						total_requests = productlog.objects.filter(product_name=product.product_name).values_list('quantity', flat=True)
						total_requests = sum(total_requests)
						total_approved = productlog.objects.filter(product_name=product.product_name).values_list('approved_quantity', flat=True)
						total_approved = sum(total_approved)
						temp['requests'] = total_requests
						temp['approved'] = total_approved
						if total_requests > 0:
							temp['approvedcent'] = round(total_approved*100/total_requests,2)
						else:
							temp['approvedcent'] = '-'
						result.append(temp)
					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'logoutStatus' : logoutStatus,
						'verified' :  user.verified,
						'result' : result,
						'name' : name,
					}
					return render(request,'home/report.html',context)
			else:
				#If user is either unverified or not an admin
				return redirect('home')
	except:
		#If user not logged in
		return redirect('home')

#Download Function no start and end date given
def export(request):
	user = useraccounts.objects.get(email=request.session['email'])
	#If user has been logged out or freezed by the admin
	if user.loginstatus == False or user.accountstatus == False:
		return redirect('logout')
	#Only for verified admin
	try:
		if user.user_type == 'Admin' and user.verified:
			result = []
			products = productlist.objects.all().order_by('product_name')
			for product in products:
				temp = {}
				temp['product'] = product.product_name
				temp['category'] = product.product_category
				query = product_operationlogs.objects.filter(product_name=product.product_name)
				temp['opening_balance'] = query[0].initial_quantity
				query = product_operationlogs.objects.filter(product_name=product.product_name).order_by('timestamp').reverse()
				temp['closing_balance'] = query[0].final_quantity
				temp['net'] = abs(temp['closing_balance']-temp['opening_balance'])
				total_requests = productlog.objects.filter(product_name=product.product_name).values_list('quantity', flat=True)
				total_requests = sum(total_requests)
				total_approved = productlog.objects.filter(product_name=product.product_name).values_list('approved_quantity', flat=True)
				total_approved = sum(total_approved)
				temp['requests'] = total_requests
				temp['approved'] = total_approved
				if total_requests > 0:
					temp['approvedcent'] = round(total_approved*100/total_requests,2)
				else:
					temp['approvedcent'] = '-'
				result.append(temp)
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment;filename="simreport.csv"'
			writer = csv.writer(response)
			writer.writerow(['Full Time Report for SIMS'])
			writer.writerow(['Product','Category','Opening Balance','Net Change','Closing Balance','Total Requests','Total Approved','%Approved'])
			for res in result:
				lis = [str(res['product']),str(res['category']),str(res['opening_balance']),str(res['net']),str(res['closing_balance']),str(res['requests']),str(res['approved']),str(res['approvedcent'])]
				writer.writerow(lis)
			return response
		else:
			return redirect('home')
	except:
		return redirect('home')

#Download function with start and end date
def exportcsv(request,start,end):
	start_date = start
	end_date = end
	#date = end_date + 1
	date = end_date
	date = date.strip()
	date = date.split('-')
	date = datetime.date(int(date[0]),int(date[1]),int(date[2]))
	date+=datetime.timedelta(days=1)
	date = str(date)

	user = useraccounts.objects.get(email=request.session['email'])
	#If user has been logged out or freezed by the admin
	if user.loginstatus == False or user.accountstatus == False:
		return redirect('logout')

	#Only for Verified Admin
	try:
		if user.user_type == 'Admin' and user.verified:
			#If end date is greater than or equal to start date
			if end_date >= start_date:
				result = []
				#get all the products
				products = productlist.objects.filter(arrival_date__lte=date).order_by('product_name')
				for product in products:
					temp = {}
					temp['product'] = product.product_name
					temp['category'] = product.product_category
					query = product_operationlogs.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date))
					#Check if query is None
					if len(query) == 0:
						query = product_operationlogs.objects.filter(product_name=product.product_name).order_by('timestamp').reverse()
						temp['opening_balance'] = query[0].final_quantity
						temp['closing_balance'] = temp['opening_balance']
						temp['net'] = abs(temp['closing_balance']-temp['opening_balance'])
						total_requests = productlog.objects.filter(product_name=product.product_name).values_list('quantity', flat=True)
						total_requests = sum(total_requests)
						total_approved = productlog.objects.filter(product_name=product.product_name).values_list('approved_quantity', flat=True)
						total_approved = sum(total_approved)
						temp['requests'] = total_requests
						temp['approved'] = total_approved
						if total_requests > 0:
							temp['approvedcent'] = round(total_approved*100/total_requests,2)
						else:
							temp['approvedcent'] = '-'
					else:
						temp['opening_balance'] = query[0].initial_quantity
						query = product_operationlogs.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).order_by('timestamp')
						count,c = len(query),0
						for q in query:
							c+=1
							if c == count:
								temp['closing_balance'] = q.final_quantity
						temp['net'] = abs(temp['closing_balance']-temp['opening_balance'])
						total_requests = productlog.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).values_list('quantity', flat=True)
						total_requests = sum(total_requests)
						total_approved = productlog.objects.filter(product_name=product.product_name,timestamp__date__range=(start_date,end_date)).values_list('approved_quantity', flat=True)
						total_approved = sum(total_approved)
						temp['requests'] = total_requests
						temp['approved'] = total_approved
						if total_requests > 0:
							temp['approvedcent'] = round(total_approved*100/total_requests,2)
						else:
							temp['approvedcent'] = '-'
					result.append(temp)
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment;filename="simreport.csv"'
				writer = csv.writer(response)
				writer.writerow(['Report between ' + start_date + ' and ' + end_date])
				writer.writerow(['Product','Category','Opening Balance','Net Change','Closing Balance','Total Requests','Total Approved','%Approved'])
				for res in result:
					lis = [str(res['product']),str(res['category']),str(res['opening_balance']),str(res['net']),str(res['closing_balance']),str(res['requests']),str(res['approved']),str(res['approvedcent'])]
					writer.writerow(lis)
				return response
			else:
				return redirect('home')
	except:
		return redirect('home')
