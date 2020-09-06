#Import Dependencies
from django.shortcuts import render,redirect
from .models import useraccounts, master_user_types
from logs.models import sessionlogs
import hashlib
import os, random, datetime
from django.utils import timezone

# Create your views here.

#Sign Up Function
def signup(request):
	logoutStatus = True
	try:
		#If email logged in, redirect to home page
		if request.session['email']:
			return redirect('home')
	except:
		#If POST method called on the sign up form
		if request.method == 'POST':
			#Getting the fields
			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
			email = request.POST.get('email')
			phone = request.POST.get('phone')
			user_role = request.POST.get('user_role')
			user_type = request.POST.get('user_type')
			password = request.POST.get('password')

			#Encode the password
			password = hashlib.sha256(password.encode()).hexdigest()

			try:
				#If User already exists
				if useraccounts.objects.get(email=email):
					message = "User Already exists!"
					all_usertypes = master_user_types.objects.all().order_by('user_type')
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'all_usertypes' : all_usertypes,
					}
					return render(request,'authentication/signup.html',context)
			except:
				#If User does not exist, and all well, redirect to OTP page
				now = datetime.datetime.now()
				user = useraccounts(first_name,
					last_name,
					email,
					phone,
					user_type,
					password,
					user_role,
					now
				)
				user.save()
				#Change the user_type delete status
				usertype = master_user_types.objects.get(user_type=user_type)
				usertype.deletestatus = False
				usertype.save()

				message = "Account created for " + str(first_name) + " " + str(last_name) + ". User Sent for verification."
				context = {
					'message' : message,
					'logoutStatus' : logoutStatus
				}

				return render(request,'authentication/login.html',context)
		else:
			#If POST method is not called, just render the sign up page
			all_usertypes = master_user_types.objects.all().order_by('user_type')
			context = {
				'logoutStatus' : logoutStatus,
				'all_usertypes' : all_usertypes,
			}
			return render(request,'authentication/signup.html',context)

#Function to log in
def login(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	try:
		#If some user already logged in, redirect to the home page
		if request.session['email']:
			return redirect('home')
	except:
		#If POST request on the login page
		if request.method == 'POST':
			#Get the Fields
			email = request.POST.get('email')
			password = request.POST.get('password')

			#Encode the password
			password = hashlib.sha256(password.encode()).hexdigest()

			try:
				#Check if the user exists in our userbase
				if useraccounts.objects.get(email=email):
					user = useraccounts.objects.get(email=email)

					#3 parameters to be checked before granting log in:
					# (1) if passwords match
					# (2) If the user is not logged in elsewhere : loginstatus
					# (3) If the user account is not freezed : accountstatus
					if user.userpassword == password and user.loginstatus == False and user.accountstatus == True:
						message = "Log in successful!"
						request.session['email'] = email	#Session Handler

						if user.user_type == 'Admin':
							admin = True
						elif user.user_type == 'User':
							non_admin = True
						else:
							dealing_admin = True

						#Change the loginstatus to True, so no other device can use this account while it is logged in here
						user.loginstatus = True
						user.save()

						#Save the login activity to the logs
						now = datetime.datetime.now(tz=timezone.utc)
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
						return redirect('home')

					else:
						#If any of the above 3 conditions do not match, show this message
						message = ["Log in unsuccessful. Please make sure that the username and the passwords are correct.", "Please make sure that the account is not logged in elsewhere.","Please make sure that your account is not freezed. In case your account is freezed, contact the Admin."]
						context = {
							'messages' : message,
							'logoutStatus' : logoutStatus
						}
						return render(request,'authentication/login.html',context)

			except:
				#If user does not exist
				message = ['The user does not exist!']
				context = {
					'messages' : message,
					'logoutStatus' : logoutStatus
				}
				return render(request,'authentication/login.html',context)
		else:
			#If no POST request, render the login page
			context = {
				'logoutStatus' : logoutStatus
			}
			return render(request,'authentication/login.html',context)

#Function to log out
def logout(request):
	logoutStatus = True
	try:
		#Get the session user object
		user = useraccounts.objects.get(email=request.session['email'])

		#Change the loginstatus to False, and save the changes
		user.loginstatus = False
		email = request.session['email']
		user.save()

		#Delete the request.session object
		del request.session['email']

		#Store the logout activity in the logs
		now = datetime.datetime.now(tz=timezone.utc)
		accounts = sessionlogs(email=email,timestamp=now,message="Logged Out.")
		accounts.save()

		context = {
			'logoutStatus' : logoutStatus
		}
		return render(request,'authentication/logout.html',context)
	except:
		#If no session exists, redirect to the log in page
		return redirect('login')

#Function to Profile Page
def profile(request):
	admin = False
	non_admin = False
	dealing_admin = False
	logoutStatus = True
	verified = False

	try:
		#If user logged in
		if request.session['email']:
			logoutStatus = False
			user = useraccounts.objects.get(email=request.session['email'])
			#If user has been logged out or freezed by the admin
			if user.loginstatus == False or user.accountstatus == False:
				return redirect('logout')

			if user.user_type == 'Admin':
				admin = True
			if user.user_type == 'User':
				non_admin = True
			if user.user_type == 'Dealing-Hand':
				dealing_admin = True
			if user.verified == True:
				verified = True

			#If request method is POST for update password
			if request.method == 'POST':
				#Get the fields
				current_password = request.POST.get('current_password')
				new_password = request.POST.get('new_password')
				confirm_password = request.POST.get('confirm_password')
				currentEmail = request.session['email']
				user = useraccounts.objects.get(email=currentEmail)

				current_password = hashlib.sha256(current_password.encode()).hexdigest()
				currentEmail = user.email
				currentName = user.first_name + " " + user.last_name
				currentPhone = user.phone
				currentUserType = user.user_type

				#If the current password matches, and the confirm and the new password field matches
				if current_password == user.userpassword and confirm_password == new_password:

					#Encode and save
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
					#If the current password does not matches, or the confirm and the new password field does not matches
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
				#If no POST request, just render the Profile page
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
		#If the user is not logged in, redirect to the log in page
		return redirect('login')
