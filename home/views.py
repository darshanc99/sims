#Import Dependencies
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from authentication.models import useraccounts, master_user_types
from logs.models import sessionlogs, product_transaction_logs
from products.models import productlog,nonconsumable_productlog
import datetime, hashlib
from django.utils import timezone
from twilio.rest import Client
from simchat.models import simmessage
from itertools import chain

#Twilio creds
account_sid = "ACa724704a972c70089e7af50aec381049"
auth_token = "cf4059a9461efced8fe78b355794fab3"
client = Client(account_sid,auth_token)

#Write your view here

#Home Function
def home(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		#Sign up remains processing
		if request.session['useremail']:
			print("Sign up remains")
			del request.session['otp']
			del request.session['first_name']
			del request.session['last_name']
			del request.session['phone']
			del request.session['user_type']
			del request.session['password']
			del request.session['user_role']
			del request.session['useremail']
			return redirect('home')
	except:
		try:
			#Forgot password processing
			if request.session['forgotemail']:
				print("Forgot Password Remains")
				del request.session['forgototp']
				del request.session['forgotemail']
				return redirect('home')
		except:
			try:
				#If user logged in
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
					elif user.user_type == 'Non-Admin':
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
					elif user.user_type == 'Dealing-Admin':
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

#Verify a user
def verify(request,email):
	#If user logged in
	try:
		if request.session['email']:
			currentEmail = request.session['email']
			user = useraccounts.objects.get(email=currentEmail)
			#Check if the user is a verified Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					user.verified = True
					to = "+91"+str(user.phone)
					user.save()
					message = "You are now a verified user. You can now enjoy the services of Smart Inventory Management System."
					client.messages.create(
						to = to,
						from_ = "+18502667962",
						body = message
					)
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
			#Check if the user is a verifed Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					#Only if the user is unverified
					if user.verified == False:
						to = "+91"+str(user.phone)
						user.delete()
						message = "Your account with SIMS couldn't be verified, as your account details seemed suspicious. Your account is hence removed from the platform."
						client.messages.create(
							to = to,
							from_ = "+18502667962",
							body = message
						)
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
			#If user is a verified Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					to = "+91"+str(user.phone)
					user.accountstatus = False
					user.save()
					now = datetime.datetime.now(tz=timezone.utc)
					message = "Account freezed for "+email
					session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
					session.save()
					message = "Your account with SIMS has been freezed. Please contact the Admin for further details."
					client.messages.create(
						to = to,
						from_ = "+18502667962",
						body = message
					)
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
			#If user is a verifed Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					user = useraccounts.objects.get(email=email)
					to = "+91"+str(user.phone)
					user.accountstatus = True
					user.save()
					now = datetime.datetime.now(tz=timezone.utc)
					message = "Account unfreezed for "+email
					session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
					session.save()
					message = "Your account with SIMS has been unfreezed. You can now use the services of SIMS seamlessly."
					client.messages.create(
						to = to,
						from_ = "+18502667962",
						body = message
					)
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
						logoutStatus = False
						context = {
							'name' : name,
							'logoutStatus' : logoutStatus,
							'admin' : admin,
							'user' : user,
							'verified' : user.verified,
							'dealing_admin' : dealing_admin,
							'non_admin' : non_admin,
						}
						now = datetime.datetime.now(tz=timezone.utc)
						message = "Account edited for "+email
						session = sessionlogs(email=request.session['email'],timestamp=now,message=message)
						session.save()
						return render(request,'home/edituser.html',context)
					else:
						#If no POST request
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

#Delete user type
def deleteusertype(request,usertype):
	#If logged in
	try:
		if request.session['email']:
			user = useraccounts.objects.get(email=request.session['email'])
			#If user is a verified Admin
			if user.user_type == 'Admin' and user.verified:
				try:
					type = master_user_types.objects.get(user_type=usertype)
					#If deletable
					if type.delete:
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
