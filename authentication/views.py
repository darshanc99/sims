#Import Dependencies
from django.shortcuts import render,redirect
from .models import useraccounts, master_user_types
from logs.models import sessionlogs
import hashlib
import os, random, datetime
from twilio.rest import Client
from django.utils import timezone
import ast

#Twilio credentials
file = open("twilio.config", "r")
contents = file.read()
dictionary = ast.literal_eval(contents)
account_sid = str(dictionary['account_sid'])
auth_token = str(dictionary['auth_token'])
sender = str(dictionary['phone'])
file.close()
client = Client(account_sid,auth_token)

# Create your views here.

#Sign Up Function
def signup(request):
	logoutStatus = True
	try:
		try:
			#For user already exists or incomplete signup attempts,
			#deleting the stored objects after refresh/redirect back to sign up by the user
			if request.session['useremail']:
				del request.session['otp']
				del request.session['first_name']
				del request.session['last_name']
				del request.session['phone']
				del request.session['user_type']
				del request.session['password']
				del request.session['user_role']
				del request.session['useremail']
				return redirect('signup')
		except:
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

			#Set the fields in the request.session object for OTP processing
			request.session['first_name'] = first_name
			request.session['last_name'] = last_name
			request.session['useremail'] = email
			request.session['phone'] = phone
			request.session['user_role'] = user_role
			request.session['user_type'] = user_type
			request.session['password'] = password

			try:
				#If User already exists
				if useraccounts.objects.get(email=email):
					message = "User Already exists!"
					all_usertypes = master_user_types.objects.all().order_by('user_type')
					print(message)
					context = {
						'message' : message,
						'logoutStatus' : logoutStatus,
						'all_usertypes' : all_usertypes,
					}
					return render(request,'authentication/signup.html',context)
			except:
				#If User does not exist, and all well, redirect to OTP page
				body = random.randint(1000,9999)
				print(request.session['useremail'],str(body) + " " + "+91"+str(phone))
				otp = str(body)
				request.session['otp'] = otp
				message = "An OTP has been sent to your mobile. Kindly enter it to verify."
				client.messages.create(
					to = "+91"+str(phone),
					from_ = sender,
					body = otp
				)
				context = {
					'message' : message,
					'logoutStatus' : logoutStatus,
					'body' : str(body)
				}
				return render(request,'authentication/otp.html',context)
		else:
			#If POST method is not called, just render the sign up page
			all_usertypes = master_user_types.objects.all().order_by('user_type')
			context = {
				'logoutStatus' : logoutStatus,
				'all_usertypes' : all_usertypes,
			}
			return render(request,'authentication/signup.html',context)

#Function to confirm the OTP
def otp(request):
	logoutStatus = True
	try:
		#If some user already logged in, redirect to homepage
		if request.session['email']:
			return redirect('home')
	except:
		try:

			#If a registration request exists in real
			if request.session['useremail']:

				#If a POST method exists
				if request.method == 'POST':
					#Get the Field
					inputotp = request.POST.get('otp')
					inputotp = str(inputotp)

					#Check if the entered OTP is correct
					if inputotp == request.session['otp']:
						logoutStatus = False
						message = "User Registered. User sent for Verification!"
						now = datetime.datetime.now()

						#Register the User with the portal
						user = useraccounts(request.session['first_name'],
							request.session['last_name'],
							request.session['useremail'],
							request.session['phone'],
							request.session['user_type'],
							request.session['password'],
							request.session['user_role'],
							now
						)
						user.save()

						#Change the user_type delete status
						usertype = master_user_types.objects.get(user_type=request.session['user_type'])
						usertype.deletestatus = False
						usertype.save()

						#Delete the request objects except 'useremail' - as required, deleted later
						del request.session['otp']
						del request.session['first_name']
						del request.session['last_name']
						del request.session['phone']
						del request.session['user_type']
						del request.session['password']
						del request.session['user_role']

						#Create a Log entry
						email = request.session['useremail']
						user = useraccounts.objects.get(email=email)
						name=user.first_name + " " + user.last_name
						message = "User created for " + name
						user.loginstatus = False
						user.save()
						del request.session['useremail']

						logoutStatus = True
						context = {
							'logoutStatus' : logoutStatus,
							'message' : message
						}
						return render(request,'authentication/login.html',context)
					else:
						#If incorrect OTP
						logoutStatus = True
						message = "Incorrect OTP. Please enter again."
						context = {
							'logoutStatus' : logoutStatus,
							'message' : message
						}
						return render(request,'authentication/otp.html',context)
				else:
					#If no POST method, just render the OTP page
					logoutStatus = True
					context = {
						'logoutStatus' : logoutStatus,
					}
					return render(request,'authentication/otp.html',context)
		except:
			#If some error occurs
			logoutStatus = True
			all_usertypes = master_user_types.objects.all().order_by('user_type')
			message = "Some error occured."
			context = {
				'message' : message,
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
		try:
			#If some user already logged in, redirect to the home page
			if request.session['email']:
				return redirect('home')
		except:
			#For incomplete signup attempts,
			#deleting the stored objects after refresh/redirect back to log in by the user
			if request.session['useremail']:
				del request.session['otp']
				del request.session['first_name']
				del request.session['last_name']
				del request.session['phone']
				del request.session['user_type']
				del request.session['password']
				del request.session['user_role']
				del request.session['useremail']
				return redirect('login')

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

#Function to forgot password Handler
def forgotpassword(request):
	logoutStatus = True
	try:
		#If user logged in, redirect to the home page
		if request.session['email']:
			return redirect('home')
	except:
		#If POST request
		if request.method == 'POST':
			#Get the field
			email = request.POST.get('email')

			try:
				#Check if the user exists in the userbase, and move to reset password function
				if useraccounts.objects.get(email=email):
					user = useraccounts.objects.get(email=email)
					body = random.randint(1000,9999)
					otp = str(body)

					#Create two objects
					request.session['forgototp'] = otp
					request.session['forgotemail'] = email

					message = 'Here is the reset password OTP:' + str(body)
					otp = str(body)
					print(email,otp,end=" ")
					phone = user.phone
					print("+91"+str(phone))
					client.messages.create(
						to = "+91"+str(phone),
						from_ = sender,
						body = message
					)
					context = {
						'message' : "OTP sent to your phone. Kindly Enter it.",
						'logoutStatus' : logoutStatus,
						'body' : str(body)
					}
					return render(request,'authentication/forgotpassword2.html',context)
			except:
				#If user does not exists
				message = 'There is no user registered with that email.'
				context = {
					'logoutStatus' : logoutStatus,
					'message' : message
				}
				return render(request,'authentication/forgotpassword1.html',context)
		else:
			#If no POST request, just render the page
			context = {
				'logoutStatus' : logoutStatus
			}
			return render(request,'authentication/forgotpassword1.html',context)

#Reset Password Function
def resetpassword(request):
	logoutStatus = True
	try:
		#If user logged in, redirect to the home page
		if request.session['email']:
			return redirect('home')
	except:
		#If POST request
		if request.method == 'POST':
			#Get the fields
			email = request.session['forgotemail']
			user = useraccounts.objects.get(email=email)
			otp = request.POST.get('otp')
			new_password = request.POST.get('new_password')
			confirm_password = request.POST.get('confirm_password')

			#Check if the OTP matches, and the new_password == confirm_password
			if otp == request.session['forgototp'] and new_password == confirm_password:
				#Set the password
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
				#If verification issues
				message = "The OTP or the passwords didn't match."
				context = {
					'message' : message,
					'logoutStatus' : logoutStatus
				}
				return render(request,'authentication/forgotpassword2.html',context)
		else:
			#If no POST request, simply render the page
			context = {
				'logoutStatus' : logoutStatus
			}
			return render(request,'authentication/forgotpassword2.html',context)
