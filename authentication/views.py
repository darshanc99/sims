from django.shortcuts import render,redirect
from .models import useraccounts
import hashlib

# Create your views here.
def signup(request):
	logoutStatus = True
	try:
		if request.session['email']:
			if request.method == 'POST':
				first_name = request.POST.get('first_name')
				last_name = request.POST.get('last_name')
				email = request.POST.get('email')
				phone = request.POST.get('phone')
				user_role = request.POST.get('user_role')
				user_type = request.POST.get('user_type')
				password = request.POST.get('password')
				password = hashlib.sha256(password.encode()).hexdigest()
				user = useraccounts(first_name,last_name,email,phone,user_type,password,user_role)
				try:
					if useraccounts.objects.get(email=email):
						message = 'User already exists!'
						currentEmail = request.session['email']
						currentUser = useraccounts.objects.get(email=currentEmail)
						currentName = currentUser.first_name+" "+currentUser.last_name
						context = {
							'message' : message,
							'name' : currentName
						}
						return render(request,'authentication/signup.html',context)
				except:
					user.save()
					message = "User Registered with SIMS!"
					currentEmail = request.session['email']
					currentUser = useraccounts.objects.get(email=currentEmail)
					currentName = currentUser.first_name+" "+currentUser.last_name
					context = {
						'message' : message,
						'name' : currentName
					}
					return render(request,'authentication/signup.html',context)
			else:
				currentEmail = request.session['email']
				currentUser = useraccounts.objects.get(email=currentEmail)
				currentName = currentUser.first_name+" "+currentUser.last_name
				context = {
					'name' : currentName
				}				
				return render(request,'authentication/signup.html',context)
	except:
		message = "You have been logged out. Please log in again!"
		context = {
			'message' : message,
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/login.html',context)

def login(request):
	logoutStatus = True
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		password = hashlib.sha256(password.encode()).hexdigest()
		try:
			if useraccounts.objects.get(email=email):
				user = useraccounts.objects.get(email=email)
				if user.userpassword == password:
					message = "Log in successful!"
					request.session['email'] = email	#Session Handler
					print(request.session['email'],message)
					return redirect('home')
				else:
					message = "Password does not match."
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus
					}
					print(message)
					return render(request,'authentication/login.html',context)
		except:
			context = {
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
		del request.session['email']
	except:
		pass
	context = {
		'logoutStatus' : logoutStatus
	}
	return render(request,'authentication/logout.html',context)

def profile(request):
	logoutStatus = True
	try:
		if request.session['email']:
			logoutStatus = False
			print("INSIDE")
			if request.method == 'POST':
				print("HAVE A POST REQUEST")
				current_password = request.POST.get('current_password')
				new_password = request.POST.get('new_password')
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
				if current_password == user.userpassword:
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
						'user_type' : currentUserType
					}
					return render(request,'authentication/profile.html',context)
				else:				
					message = "Your current passwords do not match. Couldn't update your password!"
					print(message)
					logoutStatus = False
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'name' : currentName,
						'phone' : currentPhone,
						'email' : currentEmail,
						'user_type' : currentUserType
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

def updatepassword(request):
	try:
		if request.session['email']:
			print("INSIDE")
			if request.method == 'POST':
				print("HAVE A POST REQUEST")
				current_password = request.POST.get('current_password')
				new_password = request.POST.get('new_password')
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
				if current_password == user.userpassword:
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
						'user_type' : currentUserType
					}
					return render(request,'authentication/profile.html',context)
				else:				
					message = "Your current passwords do not match. Couldn't update your password!"
					print(message)
					logoutStatus = False
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'name' : currentName,
						'phone' : currentPhone,
						'email' : currentEmail,
						'user_type' : currentUserType
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