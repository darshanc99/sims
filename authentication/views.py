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