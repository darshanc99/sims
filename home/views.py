from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from authentication.models import useraccounts

def home(request):
	try:
		if request.session['email']:
			email = request.session['email']
			user = useraccounts.objects.get(email=email)
			name=user.first_name + " " + user.last_name
			print(name)
			context = {
				'name' : name
			}
			return render(request,'home/home.html',context)
	except:
		return redirect('login')