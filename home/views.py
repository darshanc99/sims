from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from authentication.models import useraccounts


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
			print("Into the homepage")
			if user.user_type == 'Admin':
				admin = True
				print("ADMIN:",admin)
			elif user.user_type == 'Non-Admin':
				non_admin = True
				print("NONADMIN:",non_admin)
			else:
				dealing_admin = True
				print("Dealing Admin:",dealing_admin)
			print("OUT")
			logoutStatus = False
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