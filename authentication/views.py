from django.shortcuts import render,redirect
from .models import useraccounts, master_user_types
from logs.models import sessionlogs
import hashlib
import os, random, datetime
from twilio.rest import Client
from django.utils import timezone

account_sid = "ACa724704a972c70089e7af50aec381049"
auth_token = "cf4059a9461efced8fe78b355794fab3"
client = Client(account_sid,auth_token)

# Create your views here.
def signup(request):
	logoutStatus = True
	if request.method == 'POST':
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		email = request.POST.get('email')
		phone = request.POST.get('phone')
		user_role = request.POST.get('user_role')
		user_type = request.POST.get('user_type')
		password = request.POST.get('password')
		password = hashlib.sha256(password.encode()).hexdigest()
		request.session['first_name'] = first_name
		request.session['last_name'] = last_name
		request.session['email'] = email
		request.session['phone'] = phone
		request.session['user_role'] = user_role
		request.session['user_type'] = user_type
		request.session['password'] = password
		print("PASSWORD:",password)
		print("CHECK1")
		try:
			print("CHECK2")
			if useraccounts.objects.get(email=email):
				message = "User Already exists!"
				print(message)
				context = {
					'message' : message,
					'logoutStatus' : logoutStatus
				}
				return render(request,'authentication/signup.html',context)
		except:
			print("CHECK3")
			body = random.randint(1000,9999)
			print(body)
			otp = str(body)
			request.session['otp'] = otp
			print("OTP:",otp)
			message = "An OTP has been sent to your mobile. Kindly enter it to verify."
			print("+91"+str(phone))
			client.messages.create(
				to = "+91"+str(phone),
				from_ = "+18502667962",
				body = otp
			)
			context = {
				'message' : message,
				'logoutStatus' : logoutStatus,
				'body' : str(body)
			}
			return render(request,'authentication/otp.html',context)
	else:
		all_usertypes = master_user_types.objects.all().order_by('user_type')
		context = {
			'logoutStatus' : logoutStatus,
			'all_usertypes' : all_usertypes,
		}
		return render(request,'authentication/signup.html',context)

def otp(request):
	logoutStatus = True
	try:
		if request.method == 'POST':
			inputotp = request.POST.get('otp')
			inputotp = str(inputotp)
			if inputotp == request.session['otp']:
				print("CHECK4")
				logoutStatus = False
				message = "User Registered. User sent for Verification!"
				print(message)

				print(request.session['first_name'],
					request.session['last_name'],
					request.session['email'],
					request.session['phone'],
					request.session['user_type'],
					request.session['password'],
					request.session['user_role'])
				now = datetime.datetime.now()
				print(now)
				user = useraccounts(request.session['first_name'],
					request.session['last_name'],
					request.session['email'],
					request.session['phone'],
					request.session['user_type'],
					request.session['password'],
					request.session['user_role'],
					now
				)
				user.save()
				print("USER ADDED")
				request.session['email'] = request.session['email']
				del request.session['otp']
				del request.session['first_name']
				del request.session['last_name']
				del request.session['phone']
				del request.session['user_type']
				del request.session['password']
				del request.session['user_role']
				print("FINAL CHECK")
				email = request.session['email']
				user = useraccounts.objects.get(email=email)
				name=user.first_name + " " + user.last_name
				message = "User created for " + name
				user.loginstatus = False
				user.save()
				del request.session['email']
				logoutStatus = True
				context = {
					'logoutStatus' : logoutStatus,
					'message' : message
				}
				return render(request,'authentication/login.html',context)
			else:
				print("CHECK5")
				logoutStatus = True
				message = "Incorrect OTP. Please enter again."
				context = {
					'logoutStatus' : logoutStatus,
					'message' : message
				}
				return render(request,'authentication/otp.html',context)
	except:
		print("CHECK6")
		logoutStatus = True
		message = "Some error occured."
		context = {
			'message' : message,
			'loginstatus' : logoutStatus
		}
		return render(request,'authentication/signup.html',context)

def login(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		password = hashlib.sha256(password.encode()).hexdigest()
		try:
			if useraccounts.objects.get(email=email):
				user = useraccounts.objects.get(email=email)
				if user.userpassword == password and user.loginstatus == False and user.accountstatus == True:
					message = "Log in successful!"
					request.session['email'] = email	#Session Handler
					print(request.session['email'],message)
					if user.user_type == 'Admin':
						admin = True
					elif user.user_type == 'Non-Admin':
						non_admin = True
					else:
						dealing_admin = True
					user.loginstatus = True
					user.save()
					now = datetime.datetime.now(tz=timezone.utc)
					print(now)
					#accounts = sessionlogs(email = email,login_on = now,logout_on = None)
					accounts = sessionlogs(email = email,timestamp = now,message="Logged In.")
					accounts.save()
					logoutStatus = False
					name = user.first_name + " " + user.last_name
					print(name)
					context = {
						'logoutStatus' : logoutStatus,
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'message' : message,
						'name' : name
					}
					print(context)
					return redirect('home')
					#return render(request,'home/home.html',context)
				else:
					message = ["Log in unsuccessful. Please make sure that the username and the passwords are correct.", "Please make sure that the account is not logged in elsewhere.","Please make sure that your account is not freezed. In case your account is freezed, contact the Admin."]
					context = {
						'messages' : message,
						'logoutStatus' : logoutStatus
					}
					print(context)
					return render(request,'authentication/login.html',context)
		except:
			message = ['The user does not exist!']
			print(message)
			context = {
				'messages' : message,
				'logoutStatus' : logoutStatus
			}
			return render(request,'authentication/login.html',context)
	else:
		context = {
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def logout(request):
	logoutStatus = True
	try:
		user = useraccounts.objects.get(email=request.session['email'])
		user.loginstatus = False
		email = request.session['email']
		user.save()
		del request.session['email']
		now = datetime.datetime.now(tz=timezone.utc)
		print(email,None,now)
		#accounts = sessionlogs(email = email,login_on = None,logout_on = now)
		accounts = sessionlogs(email=email,timestamp=now,message="Logged Out.")
		accounts.save()
		print("logged out")
	except:
		pass
	context = {
		'logoutStatus' : logoutStatus
	}
	return render(request,'authentication/logout.html',context)

def profile(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	verified = False
	try:
		if request.session['email']:
			logoutStatus = False
			user = useraccounts.objects.get(email=request.session['email'])
			if user.user_type == 'Admin':
				admin = True
			if user.user_type == 'Non-Admin':
				non_admin = True
			if user.user_type == 'Dealing-Admin':
				dealing_admin = True
			if user.verified == True:
				verified = True
			print("INSIDE")
			if request.method == 'POST':
				print("HAVE A POST REQUEST")
				current_password = request.POST.get('current_password')
				new_password = request.POST.get('new_password')
				confirm_password = request.POST.get('confirm_password')
				currentEmail = request.session['email']
				user = useraccounts.objects.get(email=currentEmail)
				print("USER")
				current_password = hashlib.sha256(current_password.encode()).hexdigest()
				currentEmail = user.email
				currentName = user.first_name + " " + user.last_name
				currentPhone = user.phone
				currentUserType = user.user_type
				print(currentEmail,currentName,currentPhone,currentUserType,current_password)
				print("All cool")
				if current_password == user.userpassword and confirm_password == new_password:
					print("PASSWORDS CHANGE")
					new_password = hashlib.sha256(new_password.encode()).hexdigest()
					user.userpassword = new_password
					user.save()
					logoutStatus = False
					message = "Password updated!"
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'name' : currentName,
						'email' : currentEmail,
						'phone' : currentPhone,
						'user_type' : currentUserType,
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'verified' : verified
					}
					return render(request,'authentication/profile.html',context)
				else:
					message = "Your current passwords do not match, or your confirm password didn't match. Couldn't update your password!"
					print(message)
					logoutStatus = False
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'name' : currentName,
						'phone' : currentPhone,
						'email' : currentEmail,
						'user_type' : currentUserType,
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'verified' : verified
					}
					return render(request,'authentication/profile.html',context)
			else:
				currentEmail = request.session['email']
				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				currentPhone = currentUser.phone
				currentUserType = currentUser.user_type
				context = {
					'logoutStatus' : logoutStatus,
					'name' : currentName,
					'email' : currentEmail,
					'phone' : currentPhone,
					'user_type' : currentUserType,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'verified' : verified
				}
				return render(request,'authentication/profile.html',context)
	except:
		message = "You have been logged out. Please log in again!"
		logoutStatus = True
		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def updatepassword(request):
	admin = False
	non_admin = False
	dealing_admin = False
	verified = False
	logoutStatus = True
	try:
		if request.session['email']:
			print("INSIDE")
			logoutStatus = False
			if request.method == 'POST':
				print("HAVE A POST REQUEST")
				current_password = request.POST.get('current_password')
				new_password = request.POST.get('new_password')
				confirm_password = request.POST.get('confirm_password')
				currentEmail = request.session['email']
				user = useraccounts.objects.get(email=currentEmail)
				if user.user_type == 'Admin':
					admin = True
				elif user.user_type == 'Non-Admin':
					non_admin = True
				else:
					dealing_admin = True
				if user.verified == True:
					verified = True
				print("USER")
				current_password = hashlib.sha256(current_password.encode()).hexdigest()
				currentEmail = user.email
				currentName = user.first_name + " " + user.last_name
				currentPhone = user.phone
				currentUserType = user.user_type
				print(currentEmail,currentName,currentPhone,currentUserType,current_password)
				print("All cool")
				if current_password == user.userpassword and confirm_password == new_password:
					print("PASSWORDS CHANGE")
					new_password = hashlib.sha256(new_password.encode()).hexdigest()
					user.userpassword = new_password
					user.save()
					logoutStatus = False
					message = "Password updated!"
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'name' : currentName,
						'email' : currentEmail,
						'phone' : currentPhone,
						'user_type' : currentUserType,
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'verified' : verified
					}
					return render(request,'authentication/profile.html',context)
				else:
					message = "Your current passwords do not match, or your confirm password didn't match. Couldn't update your password!"
					print(message)
					logoutStatus = False
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'name' : currentName,
						'phone' : currentPhone,
						'email' : currentEmail,
						'user_type' : currentUserType,
						'admin' : admin,
						'dealing_admin' : dealing_admin,
						'non_admin' : non_admin,
						'verified' : verified
					}
					return render(request,'authentication/profile.html',context)
			else:
				currentEmail = request.session['email']
				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				currentPhone = currentUser.phone
				currentUserType = currentUser.user_type
				context = {
					'logoutStatus' : logoutStatus,
					'name' : currentName,
					'email' : currentEmail,
					'phone' : currentPhone,
					'user_type' : currentUserType
				}
				return render(request,'authentication/profile.html',context)
	except:
		message = "You have been logged out. Please log in again!"
		logoutStatus = True
		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def forgotpassword(request):
	logoutStatus = True
	if request.method == 'POST':
		email = request.POST.get('email')
		try:
			if useraccounts.objects.get(email=email):
				user = useraccounts.objects.get(email=email)
				body = random.randint(1000,9999)
				otp = str(body)
				request.session['forgototp'] = otp
				request.session['forgotemail'] = email
				message = 'Here is the reset password OTP:',otp
				otp = str(body)
				print("OTP:",otp)
				phone = user.phone
				print("+91"+str(phone))
				client.messages.create(
					to = "+91"+str(phone),
					from_ = "+18502667962",
					body = message
				)
				context = {
					'message' : "OTP sent to your phone. Kindly Enter it.",
					'logoutStatus' : logoutStatus,
					'body' : str(body)
				}
				return render(request,'authentication/forgotpassword2.html',context)
		except:
			message = 'There is no user registered with that email.'
			context = {
				'logoutStatus' : logoutStatus,
				'message' : message
			}
			return render(request,'authentication/forgotpassword1.html',context)
	else:
		context = {
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/forgotpassword1.html',context)

def resetpassword(request):
	logoutStatus = True
	if request.method == 'POST':
		email = request.session['forgotemail']
		user = useraccounts.objects.get(email=email)
		otp = request.POST.get('otp')
		new_password = request.POST.get('new_password')
		confirm_password = request.POST.get('confirm_password')
		if otp == request.session['forgototp'] and new_password == confirm_password:
			print("All correct")
			new_password = hashlib.sha256(new_password.encode()).hexdigest()
			user.userpassword = new_password
			user.save()
			del request.session['forgototp']
			del request.session['forgotemail']
			message = ["Your Password Reset is successful!"]
			context = {
				'logoutStatus' : logoutStatus,
				'messages' : message,
			}
			return render(request,'authentication/login.html',context)
		else:
			message = "The OTP or the passwords didn't match."
			context = {
				'message' : message,
				'logoutStatus' : logoutStatus
			}
			return render(request,'authentication/forgotpassword2.html',context)
	else:
		context = {
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/forgotpassword2.html',context)
