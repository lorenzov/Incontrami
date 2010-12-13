# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.contrib.auth.models import *
from incontrami.dating.models import *
import logging
import cgi


def loginfb(request):
	error = None
	logging.debug
	if request.user.is_authenticated():
		
		
	
		return HttpResponseRedirect('/')#(t.render(c))

	if request.GET:
		if 'code' in request.GET:
			args = {
				'client_id': '145417192176510',
				'redirect_uri': 'http://incontrami.euproweb.eu/login/',
				'client_secret': 'bb479280f4c5b3144dff92c770a5904a',
				'code': request.GET['code'],
			}
			url = 'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(args)
			response = cgi.parse_qs(urllib.urlopen(url).read())
			access_token = ''
			try: 
				access_token = response['access_token'][0]
			except:
				return HttpResponse(url)
                

			facebook_session = FacebookSession.objects.get_or_create(
				access_token=access_token,
			)[0]
			facebook_session.save()
			logging.debug('session')
			user = auth.authenticate(token=access_token, request = request)
			if user:
				if user.is_active:
					auth.login(request, user)
					
					
					return HttpResponseRedirect('/game/')#(t.render(c))
				else:
					error = 'AUTH_DISABLED'
			else:
				error = 'AUTH_FAILED'
		elif 'error_reason' in request.GET:
			error = 'AUTH_DENIED'
	
	return HttpResponseRedirect('https://graph.facebook.com/oauth/authorize?client_id=169893959694532&redirect_uri=http://incontrami.euproweb.eu/login/&scope=publish_stream,email,user_birthday,user_location,user_hometown&display=popup')






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
	c = RequestContext(request, {})
	t = loader.get_template('home.html')
	return HttpResponse(t.render(c))
	
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