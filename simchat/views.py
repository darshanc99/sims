from django.shortcuts import render,redirect
from authentication.models import useraccounts
from .models import simmessage
import datetime
from django.utils import timezone

# Create your views here.
def compose(request):
	logoutStatus = True
	admin = False
	non_admin = False
	dealing_admin = False
	try:
		if request.session['email']:
			logoutStatus = False
			user = useraccounts.objects.get(email=request.session['email'])
			name = user.first_name + ' ' + user.last_name
			if request.method == "POST":
				if user.user_type == 'Admin':
					admin = True
				elif user.user_type == 'Dealing-Admin':
					dealing_admin = True
				email = request.POST.get('email')
				print(email)
				if user.user_type == 'Non-Admin':
					non_admin = True
					adminmail = email
					dealingmail = email
					acount = False
					bcount = False
					userbase = useraccounts.objects.all()
					for i in userbase:
						print(i.email)
						if i.user_type == 'Admin':
							adminmail = i.email
							acount = True
						elif i.user_type == 'Dealing-Admin':
							dealingmail = i.email
							bcount = True
						if acount == True and bcount == True:
							break
					if email == 'Admin':
						email = adminmail
					if email == 'Dealing-Admin':
						email = dealingmail

				subject = request.POST.get('subject')
				body = request.POST.get('message')
				now = datetime.datetime.now(tz=timezone.utc)
				print(email,subject,body,now)
				msg = simmessage(sender=request.session['email'],receiver=email,subject=subject,body=body,timestamp=now)
				msg.save()
				message = "Message sent successfully!"
				print(message)
				context = {
					'name' : name,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'message' : message
				}
				return render(request,'simchat/compose.html',context)
			else:
				if user.user_type == 'Admin' and user.verified == True:
					admin = True
					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'name' : name,
						'logoutStatus' : logoutStatus,
					}
					return render(request,'simchat/compose.html',context)
				elif user.user_type == 'Dealing-Admin' and user.verified == True:
					dealing_admin = True
					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'name' : name,
						'logoutStatus' : logoutStatus,
					}
					return render(request,'simchat/compose.html',context)
				elif user.user_type == 'Non-Admin' and user.verified == True:
					print("IN")
					non_admin = True
					context = {
						'admin' : admin,
						'non_admin' : non_admin,
						'dealing_admin' : dealing_admin,
						'name' : name,
						'logoutStatus' : logoutStatus,
					}
					return render(request,'simchat/compose.html',context)
				else:
					user.loginstatus = False
					user.save()
					del request.session['email']
					return redirect('login')
		else:
			return redirect('login')
	except:
		user = useraccounts.objects.get(email=request.session['email'])
		user.loginstatus = False
		user.save()
		del request.session['email']
		return redirect('login')

def inbox(request):
	logoutStatus = False
	admin = False
	non_admin = False
	dealing_admin = False
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		name = user.first_name + ' ' + user.last_name
		if user.user_type == 'Admin' and user.verified == True:
			admin = True
		elif user.user_type == 'Dealing-Admin' and user.verified == True:
			dealing_admin = True
		elif user.user_type == 'Non-Admin' and user.verified == True:
			non_admin = True
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
		
		logoutStatus = False

		all_messages = simmessage.objects.all()
		my_messages = []
		for message in all_messages:
			if message.receiver == request.session['email'] and message.intrashed == False:
				my_messages.append(message)

		context = {
			'name' : name,
			'logoutStatus' : logoutStatus,
			'admin' : admin,
			'non_admin' : non_admin,
			'dealing_admin' : dealing_admin,
			'messages' : my_messages
		}	
		return render(request,'simchat/inbox.html',context)
	else:
		return redirect('login')

def sent(request):
	logoutStatus = False
	admin = False
	non_admin = False
	dealing_admin = False
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		name = user.first_name + ' ' + user.last_name
		if user.user_type == 'Admin' and user.verified == True:
			admin = True
		elif user.user_type == 'Dealing-Admin' and user.verified == True:
			dealing_admin = True
		elif user.user_type == 'Non-Admin' and user.verified == True:
			non_admin = True
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
		
		logoutStatus = False

		all_messages = simmessage.objects.all()
		my_messages = []
		for message in all_messages:
			if message.sender == request.session['email'] and message.outtrashed == False:
				my_messages.append(message)

		context = {
			'name' : name,
			'logoutStatus' : logoutStatus,
			'admin' : admin,
			'non_admin' : non_admin,
			'dealing_admin' : dealing_admin,
			'messages' : my_messages
		}	
		return render(request,'simchat/sent.html',context)
	else:
		return redirect('login')

def inboxview(request,id):
	logoutStatus = True
	if request.session['email']:
		logoutStatus = False
		admin = False
		non_admin = False
		dealing_admin = False
		user = useraccounts.objects.get(email=request.session['email'])
		if user.verified:
			name = user.first_name + ' ' + user.last_name
			msg = simmessage.objects.get(id=id)
			if msg.receiver == request.session['email']:
				if user.user_type == 'Admin':
					admin = True
				elif user.user_type == 'Dealing-Admin':
					dealing_admin = True
				else:
					non_admin = True
				msg.read = True
				msg.save()
				context = {
					'msg' : msg,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'name' : name
				}
				return render(request,'simchat/inboxview.html',context)
			else:
				return redirect('inbox')
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')

def sentview(request,id):
	logoutStatus = True
	if request.session['email']:
		logoutStatus = False
		admin = False
		non_admin = False
		dealing_admin = False
		user = useraccounts.objects.get(email=request.session['email'])
		if user.verified:
			name = user.first_name + ' ' + user.last_name
			msg = simmessage.objects.get(id=id)
			if msg.sender == request.session['email']:
				if user.user_type == 'Admin':
					admin = True
				elif user.user_type == 'Dealing-Admin':
					dealing_admin = True
				else:
					non_admin = True
				context = {
					'msg' : msg,
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'logoutStatus' : logoutStatus,
					'name' : name
				}
				return render(request,'simchat/sentview.html',context)
			else:
				return redirect('inbox')
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')

def deleteinbox(request,id):
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		msg = simmessage.objects.get(id=id)
		if msg.receiver == request.session['email']:
			msg.intrashed = True
			msg.save()
			return redirect('inbox')
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')

def deleteoutbox(request,id):
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		msg = simmessage.objects.get(id=id)
		if msg.sender == request.session['email']:
			msg.outtrashed = True
			msg.save()
			return redirect('sent')
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
			return redirect('login')
	else:
		return redirect('login')	

def replyin(request,id):
	logoutStatus = True
	admin = False
	non_admin = False
	dealing_admin = False
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		msg = simmessage.objects.get(id=id)
		if user.email == msg.receiver:
			if user.user_type == 'Admin':
				admin = True
			elif user.user_type == 'Non-Admin':
				non_admin = True
			else:
				dealing_admin = True
			logoutStatus = False
			if request.method == "POST":
				body = request.POST.get('message')
				sender = request.session['email']
				receiver = msg.sender
				subject = "Re: " + msg.subject
				timestamp = datetime.datetime.now(tz=timezone.utc)
				msg = simmessage(sender=sender,receiver=receiver,subject=subject,body=body,timestamp=timestamp)
				msg.save()
				return redirect('sent')
			else:
				name = user.first_name + ' ' + user.last_name
				subject = "Re: " + msg.subject
				to = msg.sender
				context = {
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'name' : name,
					'logoutStatus' : logoutStatus,
					'subject' : subject,
					'to' : to,
					'msg' : msg
				}
				return render(request,'simchat/replyin.html',context)
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
	else:
		return redirect('login')

def replyout(request,id):
	logoutStatus = True
	admin = False
	non_admin = False
	dealing_admin = False
	if request.session['email']:
		user = useraccounts.objects.get(email=request.session['email'])
		msg = simmessage.objects.get(id=id)
		if user.email == msg.sender:
			if user.user_type == 'Admin':
				admin = True
			elif user.user_type == 'Non-Admin':
				non_admin = True
			else:
				dealing_admin = True
			logoutStatus = False
			if request.method == "POST":
				body = request.POST.get('message')
				sender = request.session['email']
				receiver = msg.receiver
				subject = "Re: " + msg.subject
				timestamp = datetime.datetime.now(tz=timezone.utc)
				msg = simmessage(sender=sender,receiver=receiver,subject=subject,body=body,timestamp=timestamp)
				msg.save()
				return redirect('sent')
			else:
				name = user.first_name + ' ' + user.last_name
				subject = "Re: " + msg.subject
				to = msg.receiver
				context = {
					'admin' : admin,
					'non_admin' : non_admin,
					'dealing_admin' : dealing_admin,
					'name' : name,
					'logoutStatus' : logoutStatus,
					'subject' : subject,
					'to' : to,
					'msg' : msg
				}
				return render(request,'simchat/replyout.html',context)
		else:
			user.loginstatus = False
			user.save()
			del request.session['email']
	else:
		return redirect('login')