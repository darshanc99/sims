from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from authentication.models import useraccounts
from logs.models import sessionlogs
import datetime, hashlib
from django.utils import timezone
from twilio.rest import Client

account_sid = "ACa724704a972c70089e7af50aec381049"
auth_token = "cf4059a9461efced8fe78b355794fab3"
client = Client(account_sid,auth_token)

def home(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		if request.session['email']:
			email = request.session['email']
			user = useraccounts.objects.get(email=email)
			name=user.first_name + " " + user.last_name
			print(name)
			logoutStatus = False
			print("Into the homepage")
			if user.user_type == 'Admin':
				admin = True
				all_logs = sessionlogs.objects.all().order_by('timestamp').reverse()
				print(all_logs)
				print("ADMIN:",admin)
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'all_logs' : all_logs
				}
				return render(request,'home/home.html',context)
			elif user.user_type == 'Non-Admin':
				non_admin = True
				verified = user.verified
				print("NONADMIN:",non_admin)
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'verified' : verified,
					'logoutStatus' : logoutStatus
				}
				return render(request,'home/home.html',context)
			else:
				dealing_admin = True
				print("Dealing Admin:",dealing_admin)
			print("OUT")
			context = {
				'name' : name,
				'admin' : admin,
				'non_admin' : non_admin,
				'dealing_admin' : dealing_admin,
				'logoutStatus' : logoutStatus
			}
			print(context)
			return render(request,'home/home.html',context)
	except:
		return redirect('login')

def newuser(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		if request.session['email']:
			logoutStatus = False
			currentUser = useraccounts.objects.get(email=request.session['email'])
			print(currentUser.email)
			name = currentUser.first_name + ' ' + currentUser.last_name
			if currentUser.user_type == 'Admin':
				admin = True
				print(admin)
				if request.method == 'POST':
					print("POSTING")
					first_name = request.POST.get('first_name')
					last_name = request.POST.get('last_name')
					newname = first_name + ' ' + last_name
					print(newname)
					email = request.POST.get('email')
					phone = request.POST.get('phone')
					user_role = request.POST.get('user_role')
					user_type = request.POST.get('user_type')
					password = request.POST.get('password')
					password = hashlib.sha256(password.encode()).hexdigest()
					now = datetime.datetime.now(tz=timezone.utc)
					verified = True
					loginstatus = False
					print(first_name,last_name,email,phone,user_type,password,user_role,now,verified,loginstatus)
					user = useraccounts(first_name,last_name,email,phone,user_type,password,user_role,now,verified,loginstatus)
					user.save()
					print(newname)
					message = 'User created for '+ newname
					print(message)
					logoutStatus = False
					body = "Created account for "+ email
					print(body)
					accounts = sessionlogs(email=request.session['email'],timestamp=now,message=body)
					accounts.save()
					print(body)
					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'name' : name,
						'logoutStatus' : logoutStatus,
						'message' : message
					}
					print(context)
					return render(request,'home/adduser.html',context)
				else:
					print("HELLO")
					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'logoutStatus' : logoutStatus,
						'name' : name
					}
					return render(request,'home/adduser.html',context)
			else:
				currentUser.loginstatus = False
				currentUser.save()
				del request.session['email']
				return redirect('login')
	except:
		user = useraccounts.objects.get(email=request.session['email'])
		user.loginstatus = False
		user.save()
		del request.session['email']
		return redirect('login')

def viewusers(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		if request.session['email']:
			currentUser = useraccounts.objects.get(email=request.session['email'])
			if currentUser.user_type == 'Admin':
				admin = True
				all_users = useraccounts.objects.all().order_by('email')
				for user in all_users:
					if user.verified == True:
						user.verified = 'Yes'
					if user.verified == False:
						user.verified = 'No'
					if user.loginstatus == True:
						user.loginstatus = 'Online'
					if user.loginstatus == False:
						user.loginstatus = 'Offline'
				logoutStatus = False
				name = currentUser.first_name + ' ' + currentUser.last_name
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'all_users' : all_users
				}
				return render(request,'home/viewusers.html',context)
			else:
				currentUser.loginstatus = False
				currentUser.save()
				del request.session['email']
				return redirect('login')
	except:
		user = useraccounts.objects.get(email=request.session['email'])
		user.loginstatus = False
		user.save()
		del request.session['email']
		return redirect('login')

def verify(request,email):
	if request.session['email']:
		currentEmail = request.session['email']
		user = useraccounts.objects.get(email=currentEmail)
		if user.user_type == 'Admin':
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
			return redirect('viewusers')
		else:
			user = useraccounts.objects.get(email=request.session['email'])
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')

def deleteuser(request,email):
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		if user.user_type == 'Admin':
			user = useraccounts.objects.get(email=email)
			to = "+91"+str(user.phone)
			user.delete()
			message = "Your account with SIMS couldn't be verified, as your account details seemed suspicious. Your account is hence removed from the platform."
			client.messages.create(
				to = to,
				from_ = "+18502667962",
				body = message
			)
			return redirect('viewusers')
		else:
			user = useraccounts.objects.get(email=request.session['email'])
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')

def freezeuser(request,email):
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		if user.user_type == 'Admin':
			user = useraccounts.objects.get(email=email)
			to = "+91"+str(user.phone)
			user.accountstatus = False
			user.save()
			message = "Your account with SIMS has been freezed. Please contact the Admin for further details."
			client.messages.create(
				to = to,
				from_ = "+18502667962",
				body = message
			)
			return redirect('viewusers')
		else:
			user = useraccounts.objects.get(email=request.session['email'])
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')

def unfreezeuser(request,email):
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		if user.user_type == 'Admin':
			user = useraccounts.objects.get(email=email)
			to = "+91"+str(user.phone)
			user.accountstatus = True
			user.save()
			message = "Your account with SIMS has been unfreezed. You can now use the services of SIMS seamlessly."
			client.messages.create(
				to = to,
				from_ = "+18502667962",
				body = message
			)
			return redirect('viewusers')
		else:
			user = useraccounts.objects.get(email=request.session['email'])
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')