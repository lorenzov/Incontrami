from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.contrib.auth.models import *
from incontrami.dating.models import *



@login_required
def game(request):
	userprofile = None
	if request.user.get_profile().sex == 'F':
		userprofile = objects.filter(sex__exact = 'M').order_by('?')[0]
	else:
		userprofile = objects.filter(sex__exact = 'F').order_by('?')[0]
	return HttpResponseRedirect('/profile/' + str(userprofile.user.id))
	return HttpResponse('game')