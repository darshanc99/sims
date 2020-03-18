from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from authentication.models import useraccounts
from logs.models import sessionlogs
import datetime, hashlib
from django.utils import timezone

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
				print("NONADMIN:",non_admin)
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