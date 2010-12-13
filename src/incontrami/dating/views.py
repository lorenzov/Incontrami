# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.contrib.auth.models import *
from incontrami.dating.models import *

def newuser(request):
	if request.GET:
		username = request.GET['username']
		sex = request.GET['sex']
		user = User()
		user =   User.objects.create_user(username, username + '@thebeatles.com', 'password')
		user.save()
		profile = UserProfile()
		profile.user = user
		profile.save()
		profile = user.get_profile()
		profile.sex = sex
		profile.save()
		return HttpResponse('<html><head></head><body>OK<br/><a href="/newuser/">add another user</a></html></html>')
	else:
		c = RequestContext(request, {})
		t = loader.get_template('newuser.html')
		return HttpResponse(t.render(c))
		
def index(request):
	return HttpResponse('home')
	
def loginview(request):
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username = username, password = password)
		if user is not None:
			login(request, user)
		else:
			return HttpResponse('error')
		return HttpResponseRedirect('/')
	else:
		c = RequestContext(request, {})
		t = loader.get_template('login.html')
		return HttpResponse(t.render(c))